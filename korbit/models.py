from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from datetime import datetime
from math import ceil, floor

import json


Base = declarative_base()

engine = create_engine('sqlite:///korbit.db', echo=False)
Session = sessionmaker(bind=engine)

session = Session()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)


class Transaction(Base):
    """
    An example of `coin-in` transaction:
    {u'coinsDetail': {u'amount': {u'currency': u'btc', u'value': u'2.40000000'}, u'transactionId': u'482af6f1eda81617826a4326fad6fd06273c795b204c5e4658853c27f16e22c5'}, u'completedAt': 1402448277000, u'timestamp': 1402448355000, u'balances': [{u'currency': u'btc', u'value': u'8.80000000'}, {u'currency': u'krw', u'value': u'509952'}], u'type': u'coin-in', u'id': u'5539'}
    """  # noqa

    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)

    #: `sell`, `buy`, `coin-in`
    type = Column(String)

    timestamp = Column(DateTime)
    completed_at = Column(DateTime)

    fee_currency = Column(String)
    fee_value = Column(Numeric(12, 8))

    order_id = Column(Integer)
    price_currency = Column(String)
    price_value = Column(Numeric(12, 8))
    amount_currency = Column(String)
    amount_value = Column(Numeric(12, 8))

    balances = Column(Text)

    #: Auxiliary data
    # aux = Column(Text)

    def __repr__(self):
        return 'Transaction ({}, {}) {}{}@{}{}'.format(
            self.id, self.type,
            self.amount_value, self.amount_currency,
            self.price_value, self.price_currency)

    def is_profitable(self, order):
        """
        :param order: An instance of Order class
        """
        if self.type == 'buy' and order.type == 'bid':
            return self.price_value < order.price
        else:
            raise Exception('Unsupported evaluation')

    def is_marked_for_sale(self):
        """Indicate whether the purchase (type=buy) transaction has been marked
        to be sold."""
        raise NotImplementedError()

    def mark_for_sale(self):
        """Mark the purchase (type=buy) transaction to be sold."""
        raise NotImplementedError()

    @staticmethod
    def insert(json_object):
        # TODO: Refactor the following section
        transaction = Transaction()
        transaction.id = json_object['id']
        transaction.type = json_object['type']
        transaction.timestamp = datetime.fromtimestamp(
            long(json_object['timestamp']) / 1000)
        transaction.completed_at = datetime.fromtimestamp(
            long(json_object['completedAt']) / 1000)

        if 'fee' in json_object:
            transaction.fee_currency = json_object['fee']['currency']
            transaction.fee_value = json_object['fee']['value']

        if 'fillsDetail' in json_object:
            details = json_object['fillsDetail']
            transaction.order_id = details['orderId']
            transaction.price_currency = details['price']['currency']
            transaction.price_value = details['price']['value']
            transaction.amount_currency = details['amount']['currency']
            transaction.amount_value = details['amount']['value']

        if 'coinsDetail' in json_object:
            details = json_object['coinsDetail']
            transaction.amount_currency = details['amount']['currency']
            transaction.amount_value = details['amount']['value']

        transaction.balances = json.dumps(json_object['balances'])

        try:
            session.add(transaction)
            session.commit()
        except IntegrityError:
            session.rollback()

    @staticmethod
    def all(type=None, limit=None):
        """Retrieve all transactions.
        :param type: ``buy`` | ``sell``
        :param limit: Maximum number of records to retrieve
        """
        query = session.query(Transaction)

        if type is not None:
            query = query.filter_by(type=type)

        if limit is not None:
            query = query.limit(limit)

        return query

    @staticmethod
    def recent_sale_orders(limit=1):
        return session.query(Transaction).filter_by(type='sell') \
            .order_by(desc(Transaction.completed_at)).limit(limit)

    @staticmethod
    def recent_buying_orders(limit=1):
        return session.query(Transaction).filter_by(type='buy') \
            .order_by(desc(Transaction.completed_at)).limit(limit)


class Order(object):
    """A single row in the orderbook."""
    def __init__(self, type, raw):
        """Default initializer.

        :param type: An order type (`ask` or `bid`)
        :param raw: A list of three elements containing price, amount, and the
            number of orders.
        """

        self.type = type
        self.price = float(raw[0])
        self.amount = float(raw[1])
        self.order_count = int(raw[2])

    def __repr__(self):
        return 'Order ({}, {}, {}, {})'.format(
            self.type, self.price,
            self.amount, self.order_count)

    @property
    def rounded_price(self):
        """Round up or down the price to the closest 100KRW."""
        return round(self.price, -2)

    @property
    def ceilinged_price(self):
        """Round up the price to the closest 100KRW."""
        return ceil(self.price / 100.0) * 100

    @property
    def floored_price(self):
        """Round down the price to the closest 100KRW."""
        return floor(self.price / 100.0) * 100


if __name__ == '__main__':
    Base.metadata.create_all(engine)
