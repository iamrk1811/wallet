from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework import status
from accounts.models import UserWallet, StatusType, Transaction, TransactionType, IdempotentTable
from api.v1.permissions import WalletAccessPermission
from datetime import datetime
from api.v1.serializers import TransactionSerializer


class WalletInit(ViewSet):
    """
    Just to initialize wallet.
    """
    permission_classes = (AllowAny, )
    parser_classes = (JSONParser, )

    def create(self, request):
        user_wallet = None
        try:
            customer_xid = request.data.get("customer_xid")
            if not customer_xid:
                return Response(data={"msg": "customer_xid is required"}, status=status.HTTP_400_BAD_REQUEST)
            user_wallet, created = UserWallet.objects.get_or_create(customer_xid=customer_xid)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "data": {
                "token": user_wallet.token
                # currently we are using a static token
            },
            "status": "success"
        }
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class Wallet(ViewSet):
    """
    Anything related to wallet
    """
    permission_classes = [WalletAccessPermission]

    def create(self, request):
        if request.user_wallet.status != StatusType.ENABLED:
            request.user_wallet.status = True
            request.user_wallet.enabled_at = datetime.now()
            request.user_wallet.save()
        response_data = {
            "status": "success",
            "data": {
                "wallet": {
                "id": request.user_wallet.id,
                "owned_by": request.user_wallet.customer_xid,
                "status": request.user_wallet.get_status_display(),
                "enabled_at": request.user_wallet.enabled_at,
                "balance": request.user_wallet.balance
                }
            }
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

    def list(self, request):
        response_data = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        if request.user_wallet.status == StatusType.DISABLED:
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        response_data = {
            "status": "success",
            "data": {
                "wallet": {
                "id": request.user_wallet.id,
                "owned_by": request.user_wallet.customer_xid,
                "status": request.user_wallet.get_status_display(),
                "enabled_at": request.user_wallet.enabled_at,
                "balance": request.user_wallet.balance
                }
            }
        }
        return Response(data=response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="transactions", url_name="transactions")
    def transactions(self, request):
        response_data = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        if request.user_wallet.status == StatusType.DISABLED:
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        transactions = Transaction.objects.filter(user_wallet=request.user_wallet)
        serializer = TransactionSerializer(transactions, many=True)
        response_data["status"] = "success"
        response_data["data"] = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="deposits", url_name="deposits")
    def deposits(self, request):
        # desposit is only possible is wallet is enabled
        response_data = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        if request.user_wallet.status != StatusType.ENABLED:
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)

        amount = float(request.data.get("amount", 0))
        reference_id = request.data.get("reference_id", None)

        if amount <= 0:
            response_data["data"]["error"] = "Amount should be greater than zero."
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        
        # if reference_id is not unique then do not proceed
        try:
            IdempotentTable.objects.create(reference_id=reference_id, type=TransactionType.DEPOSIT)
        except Exception:
            response_data["data"]["error"] = "Duplicate reference id."
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)

        transaction = Transaction.objects.create(amount=amount, type=TransactionType.DEPOSIT, user_wallet=request.user_wallet)

        request.user_wallet.balance += amount
        request.user_wallet.save()

        responase_data = {
            "status": "success",
            "data": {
                "deposit": {
                "id": request.user_wallet.id,
                "deposited_by": request.user_wallet.customer_xid,
                "status": "success",
                "deposited_at": transaction.timestamp,
                "amount": request.user_wallet.balance,
                "reference_id": reference_id
                }
            }
        }
        return Response(data=responase_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["post"], url_path="withdrawals", url_name="withdrawals")
    def withdrawals(self, request):
         # withdrawls is only possible is wallet is enabled
        response_data = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
        if request.user_wallet.status != StatusType.ENABLED:
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)

        amount = float(request.data.get("amount", 0))
        reference_id = request.data.get("reference_id", None)

        if amount <= 0:
            response_data["data"]["error"] = "Amount should be greater than zero."
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        if amount > request.user_wallet.balance:
            response_data["data"]["error"] = "Insufficient balance."
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
    
        # if reference_id is not unique then do not proceed
        try:
            IdempotentTable.objects.create(reference_id=reference_id, type=TransactionType.WITHDRAW)
        except Exception:
            response_data["data"]["error"] = "Duplicate reference id."
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        
        request.user_wallet.balance -= amount
        request.user_wallet.save()

        transaction = Transaction.objects.create(amount=amount, type=TransactionType.WITHDRAW, user_wallet=request.user_wallet)
        response_data = {
            "status": "success",
            "data": {
                "withdrawal": {
                "id": request.user_wallet.id,
                "withdrawn_by": request.user_wallet.customer_xid,
                "status": "success",
                "withdrawn_at": transaction.timestamp,
                "amount": request.user_wallet.balance,
                "reference_id": reference_id
                }
            }
        }
        return Response(data=response_data, status=status.HTTP_201_CREATED)


    def patch(self, request, pk=None):
        is_disabled = request.data.get("is_disabled", True)
        if request.user_wallet.status != StatusType.DISABLED:
            request.user_wallet.status = StatusType.DISABLED if is_disabled else StatusType.ENABLED
            request.user_wallet.disabled_at = datetime.now()
            request.user_wallet.save()
        response_data = {
            "status": "success",
            "data": {
                "wallet": {
                "id": request.user_wallet.id,
                "owned_by": request.user_wallet.customer_xid,
                "status": request.user_wallet.get_status_display(),
                "disabled_at": request.user_wallet.disabled_at,
                "balance": request.user_wallet.balance
                }
            }
        }
        return Response(data=response_data, status=status.HTTP_200_OK)