
#routing.py
from django.urls import path,re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/stocks/', consumers.StockConsumer.as_asgi()),
    re_path(r'ws/position-stocks/$', consumers.PositionStockConsumer.as_asgi()),
]