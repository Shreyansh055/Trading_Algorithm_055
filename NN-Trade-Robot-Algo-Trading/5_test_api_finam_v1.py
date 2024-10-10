"""
In this code, we test Finam API v1 using the FinamPy library.
"""

exit(777)  # Prevents code from running, otherwise it will place an order

# Before running the script, execute the command below and configure Config.py
# git clone https://github.com/cia76/FinamPy
import time

from FinamPy.FinamPy import FinamPy
from my_config.Config import Config as ConfigAPI  # Finam API configuration file
from decimal import Decimal
from FinamPy.proto.tradeapi.v1.common_pb2 import BUY_SELL_BUY, BUY_SELL_SELL

_price = 0

def get_info_by_tickers(fp_provider, symbols):
    """Retrieve information for all tickers"""
    _ticker_info = {}
    securities = fp_provider.get_securities()  # Get all ticker information
    for board, symbol in symbols:  # Loop through all tickers
        try:
            si = next(item for item in securities.securities if item.board == board and item.code == symbol)
            decimals = si.decimals
            min_step = Decimal(10 ** -decimals * si.min_step).quantize(Decimal("1."+"0"*decimals))
            _ticker_info[symbol] = {"lot": si.lot_size, "nums": decimals, "step": min_step}
        except:
            print(f'Ticker {board}.{symbol} not found')
    return _ticker_info


def get_current_price(order_book):
    """Retrieve the nearest current ticker price from the order book"""
    global _price
    print('ask:', order_book.asks[0].price, 'bid:', order_book.bids[0].price)
    _price = order_book.asks[0].price


def get_free_money(fp_provider, client_id):
    """Retrieve information about available funds"""
    portfolio = fp_provider.get_portfolio(client_id)
    return portfolio.money[0].balance


if __name__ == '__main__':
    fp_provider = FinamPy(ConfigAPI.AccessToken)
    client_id = ConfigAPI.ClientIds[0]
    security_board = "TQBR"

    symbols = (('TQBR', 'SBER'), ('TQBR', 'VTBR'))

    # Retrieve information about all tickers
    _ticker_info = get_info_by_tickers(fp_provider, symbols=symbols)
    print("Ticker info:", _ticker_info)

    _money = get_free_money(fp_provider, client_id)
    print('Available funds:', _money)

    # Get ticker price from order book
    fp_provider.on_order_book = get_current_price
    fp_provider.subscribe_order_book("SBER", "TQBR", 'orderbook1')
    time.sleep(1)
    fp_provider.unsubscribe_order_book('orderbook1', 'SBER', 'TQBR')
    print(_price)

    # Place a buy order for SBER at 5% below the current price, rounded to the price step
    _step = _ticker_info["SBER"]["step"]
    price = (Decimal(_price * 0.95) //_step) * _step
    print(price)

    rez = fp_provider.new_order(client_id=client_id, security_board=security_board, security_code="SBER", buy_sell=BUY_SELL_BUY, quantity=1, price=price, use_credit=True)
    print("Order placed:", rez)
    print("Transaction:", rez.transaction_id)
    tr_order = rez.transaction_id

    # Cancel the order after 3 seconds
    print("Canceling the order (in 3 seconds):")
    time.sleep(3)
    rez = fp_provider.cancel_order(client_id=client_id, transaction_id=tr_order)
    print(rez)

    # Get all orders
    orders = fp_provider.get_orders(client_id).orders
    for order in orders:
        print(f'  - Order No. {order.order_no} {"Buy" if order.buy_sell == "Buy" else "Sell"} {order.security_board}.{order.security_code} {order.quantity} @ {order.price}')
    
    stop_orders = fp_provider.get_stops(client_id).stops
    for stop_order in stop_orders:
        print(f'  - Stop order No. {stop_order.stop_id} {"Buy" if stop_order.buy_sell == "Buy" else "Sell"} {stop_order.security_board}.{stop_order.security_code} {stop_order.stop_loss.quantity} @ {stop_order.stop_loss.price}')

    fp_provider.close_channel()  # Close the channel before exiting
