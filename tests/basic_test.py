from __future__ import absolute_import
from korbit.api import *
from collections import Iterable


def test_get_constants():
    constants = get_constants()

    assert 'maxBtcPrice' in constants
    assert 'maxBtcWithdrawal' in constants
    assert 'minBtcOrder' in constants
    assert 'minBtcPrice' in constants
    assert 'maxBtcOrder' in constants
    assert 'btcWithdrawalFee' in constants
    assert 'transactionFee' in constants
    assert 'krwWithdrawalFee' in constants
    assert 'minKrwWithdrawal' in constants
    assert 'minBtcWithdrawal' in constants
    assert 'maxKrwWithdrawal' in constants


def test_get_wallet():
    wallet = get_wallet()

    assert 'available' in wallet
    assert 'fee' in wallet
    # TODO: Other keys need to be tested as well


def test_get_orderbook():
    orderbook = get_orderbook()

    assert 'timestamp' in orderbook
    assert 'bids' in orderbook
    assert 'asks' in orderbook


def test_get_orderbook_by_type():
    orderbook_bids = get_orderbook('bids')

    # NOTE: Is this enough?
    assert isinstance(orderbook_bids, Iterable)

    orderbook_asks = get_orderbook('asks')

    # NOTE: Is this enough?
    assert isinstance(orderbook_asks, Iterable)


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


def test_rounded_price():
    order = Order(type='sell', raw=(500123, 0.1, 1))
    assert order.price == 500123
    assert order.rounded_price == 500100
    assert order.ceilinged_price == 500200
    assert order.floored_price == 500100
