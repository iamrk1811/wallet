from rest_framework import serializers
from accounts.models import Transaction


class TransactionSerializer(serializers.Serializer):
    transaction_type = serializers.SerializerMethodField()
    amount = serializers.CharField(required=False)
    timestamp = serializers.CharField(required=False)
    
    def get_transaction_type(self, obj):
        return obj.get_type_display()
    

