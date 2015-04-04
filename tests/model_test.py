from korbit.models import Order


def test_order_object():
    order = Order(
        order_type='bid',
        raw=[300000, 0.1, 2]
    )
    assert order.order_type == 'bid'
    assert order.price == 300000
    assert order.amount == 0.1
    assert order.order_count == 2
