from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Text
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from datetime import datetime

import json


Base = declarative_base()

engine = create_engine('sqlite:///korbit.db', echo=True)
Session = sessionmaker(bind=engine)

session = Session()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    timestamp = Column(DateTime)
    completed_at = Column(DateTime)

    fee_currency = Column(String)
    fee_value = Column(Numeric(12,8))

    order_id = Column(Integer)
    price_currency = Column(String)
    price_value = Column(Numeric(12,8))
    amount_currency = Column(String)
    amount_value = Column(Numeric(12,8))

    balances = Column(Text)

    @staticmethod
    def insert(json_object):
        # TODO: Refactor the following section
        transaction = Transaction()
        transaction.id = json_object['id']
        transaction.type = json_object['type']
        transaction.timestamp = datetime.fromtimestamp(long(json_object['timestamp']) / 1000)
        transaction.completed_at = datetime.fromtimestamp(long(json_object['completedAt']) / 1000)
        transaction.fee_currency = json_object['fee']['currency']
        transaction.fee_value = json_object['fee']['value']
        transaction.order_id = json_object['fillsDetail']['orderId']
        transaction.price_currency = json_object['fillsDetail']['price']['currency']
        transaction.price_value = json_object['fillsDetail']['price']['value']
        transaction.amount_currency = json_object['fillsDetail']['amount']['currency']
        transaction.amount_value = json_object['fillsDetail']['amount']['value']
        transaction.balances = json.dumps(json_object['balances'])

        try:
            session.add(transaction)
            session.commit()
        except IntegrityError:
            session.rollback()

    @staticmethod
    def recent_sale_orders(limit=1):
        return session.query(Transaction).filter_by(type='sell').order_by(desc(Transaction.completed_at)).limit(limit)

    @staticmethod
    def recent_buying_orders(limit=1):
        return session.query(Transaction).filter_by(type='buy').order_by(desc(Transaction.completed_at)).limit(limit)


if __name__ == '__main__':
    Base.metadata.create_all(engine)