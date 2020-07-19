from django.conf.urls import url 
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, AllowedHostsOriginValidator

from MentalMathWebsite.consumers import ChatConsumer
from django.urls import path

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("test", ChatConsumer),
                    path("MentalMathWebsite/<username>", ChatConsumer),
                    path("MentalMathWebsite/findGame", ChatConsumer),
                    path("MentalMathWebsite/<username>/<username>", ChatConsumer),
                ]
            )
        )
    )
})

