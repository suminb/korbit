from __future__ import absolute_import  

from korbit.api import get_orderbook, get_user_info

def test_get_orderbook():
	orderbook = get_orderbook()

	assert 'timestamp' in orderbook
	assert 'bids' in orderbook
	assert 'asks' in orderbook


def test_get_user_info():
	info = get_user_info()

	assert 'email' in info
	assert 'prefs' in info and type(info['prefs']) == dict
