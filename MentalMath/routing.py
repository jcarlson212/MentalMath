from django.conf.urls import url 
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, AllowedHostsOriginValidator

from MentalMathWebsite.consumers import ChatConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url("MentalMathWebsite/", ChatConsumer)
                ]
            )
        )
    )
})

#ws//ourdomain/<username> 
#