#views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Portfolio,UserProfile,Position,Order
from django.contrib.auth.decorators import login_required
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    available_funds = Portfolio.objects.get(user= request.user)
    return render(request, 'registration/profile.html',{'available_funds':available_funds})

def home(request):
    position = Position.objects.filter(portfolio=1)
    total_invested = 0
    # print(total_invested)
    for positions in position:
        total_invested += positions.quantity * positions.average_price
    # print(total_invested)
    return render(request,'index.html',{'position':position,'total_invested':total_invested})

@login_required
def buystock(request):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        symbol = request.POST.get('symbol')
        price = Decimal(request.POST.get('price'))

        # Get the user's portfolio or create one if it doesn't exist
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)

        # Check if the user already has a position for the given stock
        total_cost = price * Decimal(quantity)
        if total_cost > portfolio.cash_balance:
            return redirect('/stocks?error=insufficient_funds')

        portfolio.cash_balance -= total_cost
        portfolio.save()

        position = Position.objects.filter(portfolio=portfolio, stock_symbol=symbol).first()
        if position:
            # If the position exists, update the quantity and average price
            total_quantity = position.quantity + quantity
            total_cost = (position.average_price * position.quantity) + (price * Decimal(quantity))
            average_price = total_cost / total_quantity
            position.quantity = total_quantity
            position.average_price = average_price
            position.save()
        else:
            # If the position doesn't exist, create a new one
            position = Position.objects.create(portfolio=portfolio, stock_symbol=symbol, average_price=price, quantity=quantity)

    return redirect('stock_view')

@login_required
def sellstock(request):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        symbol = request.POST.get('symbol')
        price = Decimal(request.POST.get('price'))
        print("ssd",quantity)
        print("jkj",symbol)
        print("kj",price)

        # Ge
from django.http import JsonResponse

@login_required
def buystock(request):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        symbol = request.POST.get('symbol')
        price = Decimal(request.POST.get('price'))

        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        total_cost = price * Decimal(quantity)
        if total_cost > portfolio.cash_balance:
            return JsonResponse({'status': 'error', 'message': 'Insufficient funds'}, status=400)

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

        return JsonResponse({'status': 'success', 'message': 'Stock bought successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def sellstock(request):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        symbol = request.POST.get('symbol')
        price = Decimal(request.POST.get('price'))

        portfolio = Portfolio.objects.get(user=request.user)
        position = Position.objects.filter(portfolio=portfolio, stock_symbol=symbol).first()
        if not position or quantity > position.quantity:
            return JsonResponse({'status': 'error', 'message': 'Insufficient quantity'}, status=400)

        total_sale_amount = price * Decimal(quantity)
        portfolio.cash_balance += total_sale_amount
        portfolio.save()

        remaining_quantity = position.quantity - quantity
        if remaining_quantity == 0:
            position.delete()
        else:
            position.quantity = remaining_quantity
            position.save()

        return JsonResponse({'status': 'success', 'message': 'Stock sold successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



import json
import asyncio
import yfinance as yf
from decimal import Decimal
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async
async def fetch_stock_data():
    stock_data = {}
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
        {"name": "fino pipe", "symbol": "FINPIPE.NS"},
    ]

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
        info =stock.info
        # logo_url = stock.info.get('logo_url', '')
        # logo_url = info
        # print("thisis",info)
        # print(logo_url)
        
        stock_data[name] = {
            "price": formatted_price,
            "change": formatted_change,
            "symbol": symbol,
            # "logo_url": logo_url
        }
    
    return stock_data

@sync_to_async
def retrieve_positions(user):
    return list(Position.objects.filter(portfolio__user=user))

async def sse_stock_updates(request):
    async def event_stream(user):
        while True:
            stock_data = await fetch_stock_data()
            positions = await retrieve_positions(user)
            position_data = {}
            total_profit = 0
            for position in positions:
                symbol = position.stock_symbol
                stock = yf.Ticker(symbol)
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist.iloc[-1]['Close']
                    current_price_decimal = Decimal(str(current_price))
                    current_profit = (current_price_decimal - position.average_price) * Decimal(position.quantity)
                    current_profit_str = str(current_profit)
                    total_profit += current_profit
                    position_data[symbol] = {"current_profit": current_profit_str, "ltp": str(current_price),"quantity":position.quantity}
            total_profit_str = str(total_profit)
            data = json.dumps({"stock_data": stock_data, "position_data": position_data,"total_profit":total_profit_str})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.5)

    response = StreamingHttpResponse(event_stream(request.user), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response



@login_required
def stock_view(request):
    position = Position.objects.filter(portfolio__user=request.user)
    total_invested = 0
    # print(total_invested)
    for positions in position:
        print(positions.quantity , positions.average_price)
        total_invested += positions.quantity * positions.average_price
    return render(request, 'stock.html',{"total_invested":total_invested})


# from datetime import datetime, timedelta

# def get_historical_data(request):
#     symbol = "RELIANCE.NS"
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=365)  # Fetch last 30 days of data
#     stock = yf.Ticker(symbol)
#     hist = stock.history(start=start_date, end=end_date, interval="1d")

#     data = {
#         "date": hist.index.strftime('%Y-%m-%d').tolist(),
#         "open": hist["Open"].tolist(),
#         "high": hist["High"].tolist(),
#         "low": hist["Low"].tolist(),
#         "close": hist["Close"].tolist(),
#         "volume": hist["Volume"].tolist(),
#     }
#     return JsonResponse(data)




def get_all_stock_symbols():
    # Placeholder for the method to get all stock symbols
    # You can replace this with an API call or database query to get the actual stock symbols
    return [
        "AMJUMBO.NS", "ABINFRA.NS", "ABNINT.NS", "A2ZINFRA.NS", "AAKASH.NS",
    "AARON.NS", "AARTIDRUGS.NS", "AARTIIND.NS", "AARVEEDEN.NS", "AARVI.NS",
    "AAVAS.NS", "ABAN.NS", "ABB.NS", "POWERINDIA.NS", "ABMINTLTD.NS",
    "ACC.NS", "ACCELYA.NS", "ACCORD.NS", "ACCURACY.NS", "ACEINTEG.NS",
    "ACE.NS", "ADANIENT.NS", "ADANIGAS.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANIPOWER.NS", "ADANITRANS.NS", "ADFFOODS.NS", "ADHUNIKIND.NS", "ABCAPITAL.NS",
    "ABFRL.NS", "BIRLAMONEY.NS", "ADLABS.NS", "ADORWELD.NS", "ADROITINFO.NS",
    "ADVENZYMES.NS", "ADVANIHOTR.NS", "AEGISCHEM.NS", "AFFLE.NS", "AGARIND.NS",
    "AGCNET.NS", "AGRITECH.NS", "AGROPHOS.NS", "ATFL.NS", "AHIMSA.NS",
    "AHLADA.NS", "AHLUCONT.NS", "AIAENG.NS", "AIRAN.NS", "AIROLAM.NS",
    "AJANTPHARM.NS", "AJMERA.NS", "AJOONI.NS", "AKASH.NS", "AKG.NS",
    "AKSHOPTFBR.NS", "AKSHARCHEM.NS", "AKZOINDIA.NS", "ALANKIT.NS", "ALBERTDAVD.NS",
    "ALCHEM.NS", "ALEMBICLTD.NS", "APLLTD.NS", "ALICON.NS", "ALKALI.NS",
    "ALKEM.NS", "ALKYLAMINE.NS", "ALLCARGO.NS", "ADSL.NS", "ALLSEC.NS",
    "ALMONDZ.NS", "ALOKINDS.NS", "ALPA.NS"
    
    ]

def get_stocks_at_52_week_high(symbols):
    stocks_at_52_week_high = []
    
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        
        if hist.empty:
            continue
        
        current_price = hist['Close'].iloc[-1]
        high_52_week = hist['Close'].max()
        
        # Check if current price is equal to the 52-week high
        if current_price == high_52_week:
            stocks_at_52_week_high.append({
                "symbol": symbol,
                "current_price": current_price,
                "52_week_high": high_52_week
            })
    
    return stocks_at_52_week_high

def year_high_stocks(request):
    symbols = get_all_stock_symbols()
    
    stocks_at_52_week_high = get_stocks_at_52_week_high(symbols)
    
    context = {
        'stocks': stocks_at_52_week_high
    }
    
    return render(request, 'year_high.html', context)