from __future__ import absolute_import

from collections import Iterable

import pytest

from korbit.api import *


def test_get_constants():
    constants = get_constants()

    assert 'exchange' in constants
    assert 'btc_krw' in constants['exchange']
    assert 'eth_krw' in constants['exchange']


@pytest.mark.skip('API no longer exists')
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

    assert type(orderbook['bids']) == list
    assert type(orderbook['asks']) == list

    for order in orderbook['bids']:
        assert type(order) == Order

    for order in orderbook['asks']:
        assert type(order) == Order


def test_get_orderbook_by_type():
    orderbook_bids = get_orderbook('bids')

    # NOTE: Is this enough?
    assert isinstance(orderbook_bids, Iterable)

    orderbook_asks = get_orderbook('asks')

    # NOTE: Is this enough?
    assert isinstance(orderbook_asks, Iterable)


@pytest.mark.parametrize('currency_pair', ['btc_krw', 'eth_krw'])
def test_ticker(currency_pair):
    ticker = get_ticker(currency_pair)
    assert 'timestamp' in ticker
    assert 'last' in ticker


def test_detailed_ticker_all():
    ticker = get_detailed_ticker_all()

    currencies = ['btc_krw', 'eth_krw']
    fields = ['timestamp', 'last', 'open', 'bid', 'ask', 'low', 'high',
              'volume', 'change', 'changePercent']
    for currency in currencies:
        assert currency in ticker
        for field in fields:
            assert field in ticker[currency]


def test_get_transactions():
    transactions = get_transactions()
    assert type(transactions) == list

    for t in transactions:
        assert 'timestamp' in t
        assert 'tid' in t
        assert 'price' in t
        assert 'amount' in t


@pytest.mark.skip('API no longer exists')
def test_get_user_info():
    info = get_user_info()

    assert 'email' in info
    assert 'prefs' in info and type(info['prefs']) == dict


@pytest.mark.skip('API no longer exists')
def test_buying_order():
    # TODO: Check for the current balance before running this test case
    res = place_order(order='buy', price=100000, coin_amount=0.1)

    assert res['orderId'] is not None
    assert res['status'] == 'success'

    cancel_order(res['orderId'])


@pytest.mark.skip('API no longer exists')
def test_selling_order():
    res = place_order(order='sell', price=1000000, coin_amount=0.1)

    assert res['orderId'] is not None
    assert res['status'] == 'success'

    cancel_order(res['orderId'])


def test_rounded_price():
    order = Order(order_type='sell', raw=(500123, 0.1, 1))
    assert order.price == 500123
    assert order.rounded_price == 500100
    assert order.ceilinged_price == 500200
    assert order.floored_price == 500100
