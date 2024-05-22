import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import app_stocks.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stocks.settings')

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': URLRouter(
      app_stocks.routing.websocket_urlpatterns
    ),

})


# import os

# from channels.routing import ProtocolTypeRouter
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stocks.settings')

# application = ProtocolTypeRouter({
#   'http': get_asgi_application(),
# })