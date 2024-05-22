import json
import asyncio
import yfinance as yf
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from asgiref.sync import sync_to_async
from decimal import Decimal
from collections import deque
from .models import Position
# Define the list of top 10 companies by market capitalization on NSE
companies = [
    {"name": "Reliance Industries Ltd.", "symbol": "RELIANCE.NS"},
    {"name": "Tata Consultancy Services Ltd.", "symbol": "TCS.NS"},
    {"name": "HDFC Bank Ltd.", "symbol": "HDFCBANK.NS"},
    {"name": "Hindustan Unilever Ltd.", "symbol": "HINDUNILVR.NS"},
    {"name": "Infosys Ltd.", "symbol": "INFY.NS"},
    {"name": "ICICI Bank Ltd.", "symbol": "ICICIBANK.NS"},
    {"name": "Bharti Airtel Ltd.", "symbol": "BHARTIARTL.NS"},
    {"name": "Kotak Mahindra Bank Ltd.", "symbol": "KOTAKBANK.NS"},
    {"name": "ITC Ltd.", "symbol": "ITC.NS"},
    ]

# Function to fetch stock prices and percentage change
async def fetch_stock_data():
    stock_data = {}
    for company in companies:
        symbol = company["symbol"]
        name = company["name"]

        stock = yf.Ticker(symbol)
        hist = stock.history(period='2d')  

        prev_close = hist.iloc[-2]['Close']  
        current_close = hist.iloc[-1]['Close']  
        percent_change = ((current_close - prev_close) / prev_close) * 100

        formatted_price = "{:.2f}".format(current_close)
        formatted_change = "{:.2f}".format(percent_change)

        stock_data[name] = {"price": formatted_price, "change": formatted_change,'symbol':symbol}
    
    return stock_data





class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Initialize your stock data or subscriptions here if needed
        await self.send_stock_data()

    async def disconnect(self, close_code):
        print(f"Disconnected with close code: {close_code}")
        # Perform any cleanup actions here if needed

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'buy_stock':
                await self.process_buy_order(data)
            elif action == 'sell_stock':
                await self.process_sell_order(data)
            # ... (other actions) ...

        except Exception as e:
            print(f"Error processing order: {e}")

        # Handle other actions here
    async def send_stock_data(self):
        while True:
            try:
                stock_data = await fetch_stock_data()
                await self.send(text_data=json.dumps(stock_data))
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error sending stock data: {e}")

    @sync_to_async
    def buy_stock(self, data):
        # Extract data
        user = self.scope['user']
        quantity = int(data['quantity'])
        symbol = data['symbol']
        price = Decimal(data['price'])

        # Buy stock logic
        portfolio, _ = Portfolio.objects.get_or_create(user=user)
        total_cost = price * Decimal(quantity)
        if total_cost > portfolio.cash_balance:
            return {"status": "error", "message": "insufficient_funds"}

        portfolio.cash_balance -= total_cost
        portfolio.save()

        position = Position.objects.filter(portfolio=portfolio, stock_symbol=symbol).first()
        if position:
            total_quantity = position.quantity + quantity
            total_cost = (position.average_price * position.quantity) + (price * Decimal(quantity))
            average_price = total_cost / total_quantity
            position.quantity = total_quantity
            position.average_price = average_price
            position.save()
        else:
            position = Position.objects.create(portfolio=portfolio, stock_symbol=symbol, average_price=price, quantity=quantity)
        
        return {"status": "success"}

    @sync_to_async
    def sell_stock(self, data):
        # Extract data
        user = self.scope['user']
        quantity = int(data['quantity'])
        symbol = data['symbol']
        price = Decimal(data['price'])

        # Sell stock logic
        portfolio = Portfolio.objects.get(user=user)
        position = Position.objects.filter(portfolio=portfolio, stock_symbol=symbol).first()
        if position:
            if quantity > position.quantity:
                return {"status": "error", "message": "insufficient_quantity"}

            total_sale_amount = price * Decimal(quantity)
            portfolio.cash_balance += total_sale_amount
            portfolio.save()

            remaining_quantity = position.quantity - quantity
            if remaining_quantity == 0:
                position.delete()
            else:
                position.quantity = remaining_quantity
                position.save()
            
            return {"status": "success"}
        
        return {"status": "error", "message": "no_position"}






# class StockConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send_stock_data()

#     async def disconnect(self, close_code):
#         pass

#     async def send_stock_data(self):
#         while True:
#             try:
#                 stock_data = await fetch_stock_data()
#                 await self.send(text_data=json.dumps(stock_data))
#                 await asyncio.sleep(1)
#             except Exception as e:
#                 # Handle the exception graceafully
#                 print(f"Error sending stock data: {e}")
#                 # Optionally, you can close the WebSocket connection here
#                 # await self.close()



class PositionStockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_stock_data()

    async def disconnect(self, close_code):
        pass

    async def send_stock_data(self):
        while True:
            try:
                positions = await self.retrieve_positions()
                stock_data = {}
                ltp = 0
                for position in positions:

                    symbol = position.stock_symbol
                    stock = yf.Ticker(symbol)
                    # print(stock)
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        current_price = hist.iloc[-1]['Close']
                        ltp= current_price
                        current_price_decimal = Decimal(str(current_price))
                        current_profit = (current_price_decimal - position.average_price) * Decimal(position.quantity)
                        current_profit_str = str(current_profit)
                        stock_data[symbol] = {"current_profit": current_profit_str,"ltp":ltp}
                await self.send(text_data=json.dumps(stock_data))
                await asyncio.sleep(1)  # Adjust the interval as needed
            except Exception as e:
                print(f"Error sending stock profit data: {e}")

    @sync_to_async
    def retrieve_positions(self):
        return list(Position.objects.all())

# class PositionStockConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send_stock_data()

#     async def disconnect(self, close_code):
#         pass

#     async def send_stock_data(self):
#         while True:
#             try:
#                 positions = await self.get_positions()
#                 stock_data = {}
#                 for position in positions:
#                     symbol = position.stock_symbol
#                     stock = yf.Ticker(symbol)
#                     print(stock)
#                     # hist = stock.history(period='1d')
#                     # current_price = hist.iloc[-1]['Close']

#                     # current_price_decimal = Decimal(str(current_price))
#                     # current_profit = (current_price_decimal - position.average_price) * Decimal(position.quantity)
#                     # current_profit_str = str(current_profit)

#                     # stock_data[symbol] = {"current_profit": current_profit_str}

#                 await self.send(text_data=json.dumps(stock_data))
#             except Exception as e:
#                 print(f"Error sending stock profit data: {e}")

#     @sync_to_async
#     def get_positions(self):
#         return Position.objects.all()


#     async def retrieve_positions(self):
#         return await asyncio.to_thread(Position.objects.all)





# from .models import Position

# class PositionStockConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#         self.send_stock_data()

#     def disconnect(self, close_code):
#         pass

#     def send_stock_data(self):
#         while True:
#             try:
#                 positions = Position.objects.all()
#                 stock_data = {}
#                 for position in positions:
#                     symbol = position.stock_symbol
#                     stock = yf.Ticker(symbol)
#                     hist = stock.history(period='1d')
#                     current_price = hist.iloc[-1]['Close']

#                     # Convert current_price to Decimal
#                     current_price_decimal = Decimal(str(current_price))

#                     # Perform Decimal arithmetic to calculate profit
#                     current_profit = (current_price_decimal - position.average_price) * Decimal(position.quantity)

#                     # Convert Decimal objects to strings
#                     current_profit_str = str(current_profit)

#                     stock_data[symbol] = {"current_profit": current_profit_str}

#                 # Send serialized data
#                 self.send(text_data=json.dumps(stock_data))
#             except Exception as e:
#                 print(f"Error sending stock profit data: {e}")







# async def fetch_position_data():
#     # Fetch position data from the database
#     positions = await async_to_sync(list, Position.objects.all())
#     position_data = {}
#     for position in positions:
#         # Process position data as needed
#         # ...
#         position_data[position.stock_symbol] = {"current_profit": current_profit_str}
#     return position_data

# # Background task to periodically fetch position data
# async def background_position_fetcher(queue):
#     while True:
#         position_data = await fetch_position_data()
#         await queue.put(position_data)
#         await asyncio.sleep(3)  # Adjust the interval as needed

# class PositionStockConsumer(WebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.position_data_queue = deque()

#     async def connect(self):
#         self.accept()
#         # Start the background task to fetch position data
#         self.background_task = asyncio.create_task(background_position_fetcher(self.position_data_queue))

#     async def disconnect(self, close_code):
#         # Cancel the background task on disconnect
#         self.background_task.cancel()

#     async def receive(self, text_data=None, bytes_data=None):
#         try:
#             # Get the latest position data from the queue
#             position_data = self.position_data_queue.pop()
#             await self.send(text_data=json.dumps(position_data))
#         except IndexError:
#             # Queue is empty, wait for new data
#             pass