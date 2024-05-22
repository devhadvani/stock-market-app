
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
     path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('buy-order/', buystock, name='buy-stock'),
    path('sell-order/', sellstock, name='sell-stock'),
    path('sse/stock_view/sse/stock-updates/', sse_stock_updates, name='sse_stock_updates'),
    path('sse/stock_view/', stock_view, name='stock_view'),
    path('year_high_stocks/', year_high_stocks, name='year_high_stocks'),
    # path('get-historical-data/', get_historical_data, name='get-historical-data'),
]
