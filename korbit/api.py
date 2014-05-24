import json
import requests
import time

try:
    import config
except:
    raise Exception('Could not import config.py')


BASE_URL = 'https://api.korbit.co.kr/v1'


# FIXME: This shall be replaced with a more sophisticated caching mechanism
# in the near future
def load_dict(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def store_dict(filename, dic):
    with open(filename, 'w') as f:
        f.write(json.dumps(dic))


def get(url_suffix, **params):
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.get(url, params=params)

    # TODO: Refactor the following section to eliminate duplicated code
    # TODO: Read all response headers and put them in the Exception object
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception('{}: {}'.format(res.status_code, str(res)))


def post(url_suffix, **post_data):
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.post(url, data=post_data)

    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception('{}: {}'.format(res.status_code, str(res)))


def access_token():
    """Retrieves an access token."""
    
    token_dict = None

    try:
        # FIXME: This will cause an issue when the store token is expired
        token_dict = load_dict('token.json')
    except:
        token_dict = post('oauth2/access_token',
                          client_id=config.API_KEY,
                          client_secret=config.API_SECRET,
                          username=config.USERNAME,
                          password=config.PASSWORD,
                          grant_type='password')

    store_dict('token.json', token_dict)

    return token_dict


def nonce():
    return long(time.time() * 1000)


def constants():
    return get('constants')


def detailed_ticker():
    return get('ticker/detailed')


def user_info():
    token = access_token()
    return get('user/info', access_token=token['access_token'],
               nonce=nonce() + 100)


# TODO: Is it possible to get more than 10 transactions at a time?
def user_transactions():
    token = access_token()
    return get('user/transactions', access_token=token['access_token'],
               nonce=nonce() + 300)


def wallet():
    token = access_token()
    return get('user/wallet', access_token=token['access_token'],
               nonce=nonce() + 800)


def list_open_orders():
    token = access_token()
    return get('user/orders/open', access_token=token['access_token'],
               nonce=nonce() + 200)

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

    :param order: buy | sell
    :param price: Price per BTC
    :param currency: KRW by default. I wouldn't assume Korbit supports any other
                     currency at the moment.
    :param coin_amount: Number of coin to buy/sell. This can be a fraction.
    :param _type: limit | market
    """
    token = access_token()
    url = 'user/orders/{}'.format(order)
    return post(url, access_token=token['access_token'],
                nonce=nonce() + 400, type=_type, currency=currency,
                coin_amount=coin_amount, price=price)
