import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metazo.settings')
import django
django.setup()
from django.core.management import call_command
import livestream.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter, ProtocolTypeRouter
from django.core.asgi import get_asgi_application




asgi_app = get_asgi_application()
application = ProtocolTypeRouter(

    {
        "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            livestream.routing.websocket_urlpatterns
        )
    ),
})