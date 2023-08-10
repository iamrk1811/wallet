from rest_framework.routers import DefaultRouter
from api.v1.routers import v1_router
from julo_wallet.routers import JuloWalletRouer

api_router = JuloWalletRouer()

api_router.extend('v1', v1_router)
# in future we can add multiple version of apis, by changing it's version
# ex: api_router.extend('v2', v2_router)

