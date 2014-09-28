# -*- coding: utf-8 -*-
from korbit.models import Order
from logbook import Logger
import json
import requests
import time
import sys
import os

PROD_URL = 'https://api.korbit.co.kr/v1'
TEST_URL = 'https://api.korbit-test.com/v1'
BASE_URL = PROD_URL if os.environ.get('KORBIT_MODE') == 'prod' else TEST_URL

log = Logger('korbit')


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
    """According to the official documentation:

    Nonce & Access Token
    ````````````````````
    API 중에 v1/user 로 시작하는 API는 특정 사용자의
    계정을 접근, 변경할 수 있는 API로, 사용자 인증을 통해 발부받은 Access
    Token과 순차적으로 증가하는 양수 값인 Nonce를 지정해야 한다. Nonce는 특정
    요청이 두 번 수행되는 것을 방지하고, 하나의 계정을 두 대 이상의
    클라이언트가 동시접근하는 것을 막기 위해서, 서버상에서 마지막으로 받았던
    요청의 Nonce값보다 새로 받은 요청의 Nonce값이 더 큰 경우에만 요청을
    처리한다. Nonce는 GET요청의 경우 URL에 parameter로 전달하고, POST요청의
    경우 body에 다른 파라미터와 함께 전달한다.
    """
    cast_function = int if sys.version > '3' else long
    return cast_function(time.time() * 1000)


def get_constants():
    """Get constant values from Korbit.

    Example results:
        {
            u'maxBtcPrice': u'100000000',
            u'maxBtcWithdrawal': u'1',
            u'minBtcOrder': u'0.01',
            u'minBtcPrice': u'1000',
            u'maxBtcOrder': u'21000000',
            u'btcWithdrawalFee': u'0.00020',
            u'transactionFee': u'0.0',
            u'krwWithdrawalFee': u'1000',
            u'minKrwWithdrawal': u'2000',
            u'minBtcWithdrawal': u'0.00010',
            u'maxKrwWithdrawal': u'10000000'
        }
    """
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
    orderbook['asks'] = map(lambda x: Order('ask', x), orderbook['asks'])
    orderbook['bids'] = map(lambda x: Order('bid', x), orderbook['bids'])

    if type in ('bids', 'asks'):
        return orderbook[type]
    else:
        return orderbook


def get_detailed_ticker():
    return get('ticker/detailed')


def get_user_info():
    token = access_token()
    return get('user/info', access_token=token['access_token'],
               nonce=nonce())


# TODO: Is it possible to get more than 10 transactions at a time?
def get_user_transactions(category=None):
    """Retrieves user transactions.
    :param category: fills | fiats | coins
    """
    token = access_token()
    return get('user/transactions', access_token=token['access_token'],
               nonce=nonce())


def get_wallet():
    """
    Example results:
        {
            u'available': [
                {u'currency': u'krw', u'value': u'2278998'},
                {u'currency': u'btc', u'value': u'4.90000000'}
            ],
            u'fee': u'0.0',
            u'pendingNonmemberOut': [
                {u'currency': u'krw', u'value': u'0'},
                {u'currency': u'btc', u'value': u'0'}
            ],
            u'pendingOrders': [
                {u'currency': u'krw', u'value': u'0'},
                {u'currency': u'btc', u'value': u'0'}
            ],
            u'pendingOut': [
                {u'currency': u'krw', u'value': u'0'},
                {u'currency': u'btc', u'value': u'0'}
            ],
            u'in': [
                {u'alias': u'default',
                 u'address': {u'address': u'(bitcoin wallet address)'},
                 u'currency': u'btc'}
            ],
            u'balance': [
                {u'currency': u'krw', u'value': u'2278998'},
                {u'currency': u'btc', u'value': u'4.90000000'}
            ],
            u'out': []
        }
    """
    token = access_token()
    return get('user/wallet', access_token=token['access_token'],
               nonce=nonce())


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
                 nonce=nonce())

    if order_type is not None:
        orders = filter(lambda x: x['type'] == order_type, orders)

    return orders


def cancel_order(order_id):
    token = access_token()
    return post('user/orders/cancel', access_token=token['access_token'],
                nonce=nonce(), id=order_id)


def cancel_all_orders():
    """Cancel all open orders.
    TODO: Needs to be revised. Korbit provides an API call to cancel multiple
    orders."""
    orders = get_open_orders()

    return map(cancel_order, [order['id'] for order in orders])


def place_order(order='buy', price=0.0, currency='krw', coin_amount=0.0,
                order_type='limit'):
    """Place an order.

    :param order: ``buy`` | ``sell``
    :param price: Price per BTC
    :param currency: KRW by default. I wouldn't assume Korbit supports any other
                     currency at the moment.
    :param coin_amount: Number of coin to buy/sell. This can be a fraction.
    :param order_type: ``limit`` (at a specified price) | ``market`` (at the
                       market price)
    """
    # price must be an integer
    price = int(price)

    log.info('Placing a {} order for {}BTC at {}{}'.format(
             order, coin_amount, price, currency.upper()))

    token = access_token()
    url = 'user/orders/{}'.format(order)
    return post(url, access_token=token['access_token'],
                nonce=nonce(), type=order_type, currency=currency,
                coin_amount=coin_amount, price=price)
