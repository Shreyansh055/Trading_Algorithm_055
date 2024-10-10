"""
    In this code, we are testing the Finam API v2, the finam_trade_api library.

"""

exit(777)  # to prevent the code from running, otherwise it will place an order

import time
from decimal import Decimal
from my_config.Config import Config
from finam_trade_api.client import Client
from finam_trade_api.portfolio.model import PortfolioRequestModel
from finam_trade_api.order.model import (
    BoardType,
    CreateOrderRequestModel,
    CreateStopOrderRequestModel,
    DelOrderModel,
    OrdersRequestModel,
    OrderType,
    PropertyType,
    StopLossModel,
    StopQuantity,
    StopQuantityUnits,
    TakeProfitModel
)

token = Config.AccessToken
client_id = Config.ClientIds[0]
client = Client(token)


async def get_all_data():
    return await client.securities.get_data()


async def get_data_by_code(code: str):
    return await client.securities.get_data(code)


async def get_data_by_codes(board: str, tickers: list):
    """Get information about all tickers"""
    _ticker_info = {}
    _all_info = await client.securities.get_data()
    for security in _all_info.data.securities:
        if security.code in tickers and security.board == board:
            decimals = int(security.decimals)
            min_step = security.minStep
            min_step = Decimal(10 ** -decimals * min_step).quantize(Decimal("1." + "0" * decimals))
            _ticker_info[security.code] = {"lot": int(security.lotSize), "nums": decimals, "step": min_step}
    return _ticker_info


async def get_portfolio():
    """Get information on how much free money we have"""
    params = PortfolioRequestModel(clientId=client_id)
    _portfolio_info = await client.portfolio.get_portfolio(params)
    _equity = _portfolio_info.data.equity
    _money_in_pos = 0
    for position in _portfolio_info.data.positions:
        _money_in_pos += position.equity
    return _equity - _money_in_pos


async def create_order(ticker: str, buy_sell: OrderType, quantity: int, price: float, use_credit: bool = False):
    """Function to place an order"""
    payload = CreateOrderRequestModel(
        clientId=client_id,
        securityBoard=BoardType.TQBR,
        securityCode=ticker,
        buySell=buy_sell,
        quantity=quantity,
        price=price,
        useCredit=use_credit,
        property=PropertyType.PutInQueue,
        condition=None,
        validateBefore=None,
    )
    return await client.orders.create_order(payload)


async def del_order(transaction_id: str):
    """Function to cancel an order"""
    params = DelOrderModel(clientId=client_id, transactionId=transaction_id)
    return await client.orders.del_order(params)


async def get_orders():
    """Function to get orders"""
    params = OrdersRequestModel(
        clientId=client_id,
        includeActive="true",
        includeMatched="true",
    )
    return await client.orders.get_orders(params)


if __name__ == '__main__':
    import asyncio

    # print(asyncio.run(get_all_data()))
    # code_ = "SBER"
    # print(asyncio.run(get_data_by_code(code_)))

    # Get information about all tickers
    tickers = ['SBER', 'VTBR']
    _ticker_info = asyncio.run(get_data_by_codes(board="TQBR", tickers=tickers))
    print("Information on tickers:", _ticker_info)

    _money = asyncio.run(get_portfolio())
    print('Free funds:', _money)

    # place an order to buy SBER
    _order = asyncio.run(create_order(ticker="SBER", buy_sell=OrderType.Buy, quantity=1, price=230.05, use_credit=True))
    print(_order)
    print(_order.data.transactionId)
    tr_order = _order.data.transactionId

    # cancel this order after 3 seconds
    print("Canceling the order (in 3 seconds):")
    time.sleep(3)
    rez = asyncio.run(del_order(transaction_id=tr_order))
    print(rez)

    # get orders
    print(asyncio.run(get_orders()))
