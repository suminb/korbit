from korbit.models import Order


def test_order_object1():
    order = Order(
        order_type='bid',
        raw=[300000, 0.1, 2]
    )
    assert order.order_type == 'bid'
    assert order.price == 300000
    assert order.amount == 0.1
    assert order.order_count == 2


def test_order_object2():
    order = Order(
        order_type='ask',
        price=400000,
        amount=0.2,
        order_count=3
    )
    assert order.order_type == 'ask'
    assert order.price == 400000
    assert order.amount == 0.2
    assert order.order_count == 3
