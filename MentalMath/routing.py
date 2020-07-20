from django.conf.urls import url 
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, AllowedHostsOriginValidator

from MentalMathWebsite.consumers import ChatConsumer, FindGameConsumer, GameConsumer, SoloGameConsumer
from django.urls import path

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("test", ChatConsumer),
                    path("MentalMathWebsite/findGame", FindGameConsumer),
                    path("MentalMathWebsite/<username1>/<username2>", GameConsumer),
                    path("MentalMathWebsite/<username>", SoloGameConsumer)
                ]
            )
        )
    )
})

