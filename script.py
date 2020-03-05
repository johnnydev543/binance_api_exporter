import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
from binance.client import Client

API_KEY = "hQFQVuu78HvooYCQh0vvGs7RRkscDvCMaTnESBLXWZvcCDWGnLnkL6kNCAEsbeHS"
API_SECRET = "9FS3yUCQD6Ancz8FqhTfbrPe65vbU2nqGA5wbE7laLJtHuS8U9y7q4grxW3bzs7c"
client = Client(API_KEY, API_SECRET)

# lending endpoint is not implemented in the package,
# so we need to force it to use the url and version we want
client.API_URL = 'https://api.binance.com/sapi'
client.PRIVATE_API_VERSION = "v1"

class BinanceLendingsCollector(object):

    def collect(self):

        params = {}
        lendings = client._get("lending/daily/product/list",
                               True, client.PUBLIC_API_VERSION, data=params)

        # The metrics we want to export.
        statuses = ['avgAnnualInterestRate', 'purchasedAmount', 'upLimit']

        metrics = {}

        # use "for loop" to create gauge list
        for s in statuses:
            metrics[s] = GaugeMetricFamily(
                'binance_lending_{0}'.format(s),
                'Binance API lendings product ' + s + ' data',
                labels=["asset"])

        # just get the value which only in the statuses list
        for product in lendings:
            asset_name = product.get('asset')

            for key in product:
                if key in statuses:
                    metrics[key].add_metric([asset_name], product.get(key, 0))

        for m in metrics.values():
            yield m


if __name__ == "__main__":

    REGISTRY.register(BinanceLendingsCollector())
    start_http_server(5000)
    while True:
        time.sleep(10)
