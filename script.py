import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
from binance.client import Client
API_KEY = "hQFQVuu78HvooYCQh0vvGs7RRkscDvCMaTnESBLXWZvcCDWGnLnkL6kNCAEsbeHS"
API_SECRET = "9FS3yUCQD6Ancz8FqhTfbrPe65vbU2nqGA5wbE7laLJtHuS8U9y7q4grxW3bzs7c"

client = Client(API_KEY, API_SECRET)
params = {}  # {'status': 'ALL'}

# there is no lending endpoint api by far, so this is a tradeoff resort
client.API_URL = 'https://api.binance.com/sapi'
client.PRIVATE_API_VERSION = "v1"

lendings = client._get("lending/daily/product/list", True, client.PUBLIC_API_VERSION, data=params);

class JenkinsCollector(object):
    def collect(self):
        metric_avgAnnualInterestRate = GaugeMetricFamily(
            'binance_lending_avgAnnualInterestRate',
            'Binance API lending avgerage annual interestRate',
            labels=["asset"])

        metric_purchasedAmount = GaugeMetricFamily(
            'binance_lending_purchasedAmount',
            'Binance API lending purchased amount',
            labels=["asset"])

        metric_upLimit = GaugeMetricFamily(
            'binance_lending_upLimit',
            'Binance API lending upLimit',
            labels=["asset"])

        for asset in lendings:
            name = asset['asset']

            # If there's a null result, we want to export a null.
            avgAnnualInterestRate = asset['avgAnnualInterestRate'] or null
            purchasedAmount = asset['purchasedAmount'] or null
            upLimit = asset['upLimit'] or null

            metric_avgAnnualInterestRate.add_metric([name], avgAnnualInterestRate)
            metric_purchasedAmount.add_metric([name], purchasedAmount)
            metric_upLimit.add_metric([name], upLimit)

        yield metric_avgAnnualInterestRate
        yield metric_purchasedAmount
        yield metric_upLimit


if __name__ == '__main__':
    REGISTRY.register(JenkinsCollector())
    start_http_server(5000)
    while True:
        time.sleep(10)
