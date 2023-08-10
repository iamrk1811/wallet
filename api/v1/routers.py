from julo_wallet.routers import JuloWalletRouer
from api.v1 import viewsets

v1_router = JuloWalletRouer()

v1_router.register(r'init', viewsets.WalletInit, basename="wallet_init")
v1_router.register(r'wallet', viewsets.Wallet, basename="wallet")