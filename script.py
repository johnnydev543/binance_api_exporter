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

API_KEY = config['api']['API_KEY']
API_SECRET = config['api']['API_SECRET']

client = Client(API_KEY, API_SECRET)

class BinanceAPICollector(object):

    def collect(self):

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


if __name__ == "__main__":

    REGISTRY.register(BinanceAPICollector())
    start_http_server(5000)
    while True:
        time.sleep(10)
