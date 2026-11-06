from order_app.constants import is_supported_currency


def test_currency_smoke():
    is_supported_currency("usd")
