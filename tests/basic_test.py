from __future__ import absolute_import
from korbit.api import *


def test_get_orderbook():
    orderbook = get_orderbook()

    assert 'timestamp' in orderbook
    assert 'bids' in orderbook
    assert 'asks' in orderbook


def test_get_orderbook_by_type():
    orderbook_bids = get_orderbook('bids')

    # NOTE: Is this enough?
    assert isinstance(orderbook_bids, list)

    orderbook_asks = get_orderbook('asks')

    # NOTE: Is this enough?
    assert isinstance(orderbook_asks, list)


def test_get_user_info():
    info = get_user_info()

    assert 'email' in info
    assert 'prefs' in info and type(info['prefs']) == dict


def test_buying_order():
    # TODO: Check for the current balance before running this test case
    res = place_order(order='buy', price=100000, coin_amount=0.1)

    assert res['orderId'] is not None
    assert res['status'] == 'success'

    cancel_order(res['orderId'])


def test_selling_order():
    res = place_order(order='sell', price=1000000, coin_amount=0.1)

    assert res['orderId'] is not None
    assert res['status'] == 'success'

    cancel_order(res['orderId'])
