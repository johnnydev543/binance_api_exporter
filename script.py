import time, os
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
from binance.client import Client
import configparser
import requests
import json


# reads the configuration from settings file
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'config.ini') 
try:
    config.read(config_file)
except:
    print('Error! Please make sure that "config.ini" file exists and properly set.')
    exit(1)

API_KEY          = config['api']['API_KEY']
API_SECRET       = config['api']['API_SECRET']
EXPORTER_TICKER  = config['exporter']['ticker']
EXPORTER_LENDING = config['exporter']['lending']
EXPORTER_CUSTOMIZED_FIXED = config['exporter']['customized_fixed']

client = Client(API_KEY, API_SECRET)

class BinanceAPICollector(object):

    def collect(self):

        if EXPORTER_TICKER == 'yes':

            tickers = ['BTCUSDT', 'ETHUSDT']

            ticker_metrics = GaugeMetricFamily(
                'binance_ticker_price',
                'Binance API ticker price',
                labels=['symbol']
            )

            for t in tickers:
                ticker = client.get_symbol_ticker(symbol=t)
                price = ticker.get('price', None)
                ticker_metrics.add_metric([t], price)

            yield ticker_metrics

        if EXPORTER_LENDING == 'yes':

            lendings = client.get_lending_product_list(timestamp=time.time())

            # The metrics we want to export.
            statuses = ['avgAnnualInterestRate', 'purchasedAmount', 'upLimit']

            lending_metrics = {}

            # use "for loop" to create gauge list
            for s in statuses:
                lending_metrics[s] = GaugeMetricFamily(
                    'binance_lending_{0}'.format(s),
                    'Binance API lendings product ' + s + ' data',
                    labels=["asset"])

            # just get the value which only in the statuses list
            for product in lendings:
                asset_name = product.get('asset')

                for key in product:
                    if key in statuses:
                        lending_metrics[key].add_metric([asset_name], product.get(key, 0))

            for m in lending_metrics.values():
                yield m


        if EXPORTER_CUSTOMIZED_FIXED == 'yes':
            projects = client.get_fixed_activity_project_list(
                    type='CUSTOMIZED_FIXED',
                    status='ALL',
                    timestamp=time.time()
                    )
            # print(projects)
            customized_fixed_purchased_metrics = GaugeMetricFamily(
                'binance_customized_fixed_purchased',
                'Binance API Customized Fixed Project purchased data',
                labels=['projectId', 'duration', 'asset']
            )
            customized_fixed_uplimit_metrics = GaugeMetricFamily(
                'binance_customized_fixed_uplimit',
                'Binance API Customized Fixed Project uplimit data',
                labels=['projectId', 'duration', 'asset']
            )
            customized_fixed_rate_metrics = GaugeMetricFamily(
                'binance_customized_fixed_rate',
                'Binance API Customized Fixed Project interest rate data',
                labels=['projectId', 'duration', 'asset']
            )

            for project in projects:
                asset         = project.get('asset', None)
                duration      = project.get('duration', None)
                lotSize       = project.get('lotSize', None)
                lotsPurchased = project.get('lotsPurchased', None)
                lotsUpLimit   = project.get('lotsUpLimit', None)
                projectId     = project.get('projectId', None)
                interestRate  = project.get('interestRate', None)

                purchased = int(lotsPurchased) * int(lotSize)
                uplimit = int(lotsUpLimit) * int(lotSize)

                customized_fixed_purchased_metrics.add_metric([projectId, str(duration), asset], purchased)
                customized_fixed_uplimit_metrics.add_metric([projectId, str(duration), asset], uplimit)
                customized_fixed_rate_metrics.add_metric([projectId, str(duration), asset], interestRate)

            yield customized_fixed_purchased_metrics
            yield customized_fixed_uplimit_metrics
            yield customized_fixed_rate_metrics

if __name__ == "__main__":

    REGISTRY.register(BinanceAPICollector())
    start_http_server(5000)
    while True:
        time.sleep(10)
