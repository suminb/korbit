import json
import requests
import time
import sys
import os
import logging

PROD_URL = 'https://api.korbit.co.kr/v1'
TEST_URL = 'https://api-test.korbit.co.kr/v1'
BASE_URL = PROD_URL if os.environ.get('KORBIT_MODE') == 'prod' else TEST_URL

logger = logging.getLogger('korbit')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# FIXME: This shall be replaced with a more sophisticated caching mechanism
# in the near future
def load_dict(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def store_dict(filename, dic):
    with open(filename, 'w') as f:
        f.write(json.dumps(dic))


def get(url_suffix, **params):
    """Initiates an HTTP GET request."""
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.get(url, params=params)

    # TODO: Refactor the following section to eliminate duplicated code
    # TODO: Read all response headers and put them in the Exception object
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception('{}: {}'.format(res.status_code, str(res)))


def post(url_suffix, **post_data):
    """Initiates an HTTP POST request."""
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.post(url, data=post_data)

    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception('{}: {} {}'.format(res.status_code, str(res.headers),
                        str(res)))


def access_token():
    """Retrieves an access token."""

    def has_expired(token_dict):
        """Determines whether a token has expired."""

        issued_at = token_dict['issued_at']
        expires_in = token_dict['expires_in']

        return issued_at + expires_in < time.time()

    def request_token():
        """Requests a new token."""
        token_dict = post('oauth2/access_token',
                          client_id=os.environ['KORBIT_API_KEY'],
                          client_secret=os.environ['KORBIT_API_SECRET'],
                          username=os.environ['KORBIT_API_USERNAME'],
                          password=os.environ['KORBIT_API_PASSWORD'],
                          grant_type='password')

        token_dict['issued_at'] = time.time()  # current Unix time

        store_dict('token.json', token_dict)

        return token_dict

    token_dict = None

    try:
        # FIXME: This will cause an issue when the store token is expired
        token_dict = load_dict('token.json')

        if has_expired(token_dict):
            token_dict = request_token()
    except:
        token_dict = request_token()

    return token_dict


def nonce():
    cast_function = int if sys.version > '3' else long
    return cast_function(time.time() * 1000)


def get_constants():
    return get('constants')


def get_orderbook(type=None):
    """Retrieves all open orders (public).

    Example results

    .. code-block:: python

        {
            u'timestamp': 1386135077000,
            u'bids': [
                [
                    u'677300',
                    u'3.50000000',
                    u'1'
                ],
                ...
            ],
            u'asks': [
                [
                    u'679500',
                    u'0.15854124',
                    u'2'
                ],
                ...
            ]
        }

    For ``bids`` and ``asks`` tuples,

    * First column represents the bidding or asking price per BTC
    * Second column represents the total quantity (BTC)
    * Third column represents the total number of orders of that price

    """
    orderbook = get('orderbook')

    if type in ('bids', 'asks'):
        return orderbook[type]
    else:
        return orderbook


def get_detailed_ticker():
    return get('ticker/detailed')


def get_user_info():
    token = access_token()
    return get('user/info', access_token=token['access_token'],
               nonce=nonce() + 100)


# TODO: Is it possible to get more than 10 transactions at a time?
def get_user_transactions(category=None):
    """Retrieves user transactions.
    :param category: fills | fiats | coins
    """
    token = access_token()
    return get('user/transactions', access_token=token['access_token'],
               nonce=nonce() + 300)


def get_wallet():
    token = access_token()
    return get('user/wallet', access_token=token['access_token'],
               nonce=nonce() + 800)


def get_open_orders(order_type):
    """Retrieves open orders.

    :param order_type: ``None`` | ``bid`` | ``ask``

    Example results

    .. code-block:: python

        [
            {
                u'open': {
                    u'currency': u'btc',
                    u'value': u'0.02000000'
                },
                u'timestamp': 1402214947000,
                u'price': {
                    u'currency': u'krw',
                    u'value': u'500000'
                },
                u'total': {
                    u'currency': u'btc',
                    u'value': u'0.02000000'
                },
                u'type': u'bid',
                u'id': u'138502'
            },
            {
                u'open': {
                    u'currency': u'btc',
                    u'value': u'0.01000000'
                },
                u'timestamp': 1402214920000,
                u'price': {
                    u'currency': u'krw',
                    u'value': u'600000'
                },
                u'total': {
                    u'currency': u'btc',
                    u'value': u'0.01000000'
                },
                u'type': u'bid',
                u'id': u'138501'
            }
        ]

    """
    token = access_token()
    orders = get('user/orders/open', access_token=token['access_token'],
               nonce=nonce() + 200)

    if order_type is not None:
        orders = filter(lambda x: x['type'] == order_type, orders)

    return orders


def cancel_order(order_id):
    token = access_token()
    return post('user/orders/cancel', access_token=token['access_token'],
                nonce=nonce() + 600, id=order_id)


def cancel_all_orders():
    """Cancel all open orders.
    TODO: Needs to be revised. Korbit provides an API call to cancel multiple
    orders."""
    orders = list_open_orders()

    return map(cancel_order, [order['id'] for order in orders])


def place_order(order='buy', price=0.0, currency='krw', coin_amount=0.0,
                _type='limit'):
    """Place an order.

    :param order: ``buy`` | ``sell``
    :param price: Price per BTC
    :param currency: KRW by default. I wouldn't assume Korbit supports any other
                     currency at the moment.
    :param coin_amount: Number of coin to buy/sell. This can be a fraction.
    :param _type: ``limit`` | ``market``
    """
    logger.info('Placing a {} order for {}BTC at {}{}'.format(
                order, coin_amount, price, currency.upper()))

    token = access_token()
    url = 'user/orders/{}'.format(order)
    return post(url, access_token=token['access_token'],
                nonce=nonce() + 400, type=_type, currency=currency,
                coin_amount=coin_amount, price=price)
