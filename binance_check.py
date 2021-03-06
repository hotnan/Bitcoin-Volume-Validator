from binance.client import Client
client = Client("DdEn5fpqEAekNJCVYmflOY9pLfIozLTjU4qXm5HqB9vyFh9PAB7LNdBWPjrkHf43", "c5NjpuJPGYgQZ60ZUXE3z6FQTV3YVOTNVz5JZ5aW2ST3uTJM65mykaFjCDMhPa1D")

from binance.websockets import BinanceSocketManager
import time
from pprint import pprint
import os

last_bid = 0
last_ask = 0 
faked_volume = 0
legit_volume = 0
last_trade_time = 0 


def process_message(msg):
    # os.system('clear')
    global last_bid, last_ask, faked_volume, legit_volume, last_trade_time

    # Is a order book stream update
    # Since the 'A' key is only present in the book ticker stream
    if 'A' in msg:
        last_bid = msg['b']
        last_ask = msg['a']
        print('\u001b[38;5;83m', last_bid, '\033[0m', '\u001b[38;5;244m', '----', '\033[0m', '\u001b[38;5;196m', last_ask, '\033[0m')

    # Is a trade stream update 
    else:
        trade_time = msg['T'] 

        # Check this trade time is AFTEr the last trade time
        # This ensures the trades we're seeing are indeed in order
        # and not some lagged trade coming through from some post settlment process etc on binances end
        # This is in miliseconds which does not actually have enough precision 
        if trade_time < last_trade_time:
            print('\033[96m', 'ERROR, Trade Time does not follow chronological order', '\033[0m')

        # Check if the trade occured above the last best bid, and below the last best ask
        # Thus occured 'between the spread' 
        if ( ( msg['p'] > last_bid ) and (msg['p'] < last_ask) ):
            print('\033[93m', '-- EXECUTION BETWEEN SPREAD (_o_): ', msg['T'], '--', msg['p'], 'for', msg['q'], '\033[0m')
            faked_volume = faked_volume + float(msg['q'])
        else:
            print('\u001b[38;5;244m', '-- Legit Trade: ', msg['T'], '--', msg['p'], 'for', msg['q'], '\033[0m')
            legit_volume = legit_volume + float(msg['q'])

        print('\033[95m', 'total fake: ', faked_volume, ' BTC', '\033[0m')
        print('\033[95m', 'total legit: ', legit_volume, ' BTC', '\033[0m')

bm = BinanceSocketManager(client)

# Real time book ticker stream
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#individual-symbol-book-ticker-streams
# https://github.com/sammchardy/python-binance/blob/c66695a785e8d3cf0975d09b624f79772dac4115/binance/websockets.py#L409
bm.start_symbol_book_ticker_socket('BTCUSDT', process_message)

# Real time trade execution feed
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#trade-streams
# https://github.com/sammchardy/python-binance/blob/c66695a785e8d3cf0975d09b624f79772dac4115/binance/websockets.py#L254
bm.start_trade_socket('BTCUSDT', process_message)
bm.start()



