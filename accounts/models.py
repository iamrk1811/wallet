from django.db import models
import uuid


class StatusType:
    ENABLED = 1
    DISABLED = 2

    CHOICES = (
        (ENABLED, "enabled"),
        (DISABLED, "disabled")
    )



class TransactionType:
    DEPOSIT = 1
    WITHDRAW = 2

    CHOICES = (
        (DEPOSIT, "deposit"),
        (WITHDRAW, "withdraw")
    )


class UserWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_xid = models.CharField(max_length=100, null=False, blank=False, unique=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=StatusType.CHOICES, blank=True, null=True, default=StatusType.DISABLED)
    enabled_at = models.DateTimeField(blank=True, null=True)
    disabled_at = models.DateTimeField(blank=True, null=True)
    balance = models.FloatField(blank=True, null=True, default=0)

    def __str__(self) -> str:
        return self.customer_xid

    def save(self, *args, **kwargs):
        if not self.token:
            # token will be initialized only once
            self.token = str(uuid.uuid4())
        super(UserWallet, self).save(*args, **kwargs)
    

class Transaction(models.Model):
    type = models.PositiveSmallIntegerField(choices=TransactionType.CHOICES, blank=True, null=True)
    amount = models.FloatField(default=0)
    user_wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class IdempotentTable(models.Model):
    # trying to mimic Idempotency, since we have unique reference_id,
    # although we should other databse which supports TTL (Time To Live), like mongoDB or redis
    reference_id = models.CharField(max_length=100, unique=True)
    type = models.PositiveSmallIntegerField(choices=TransactionType.CHOICES, blank=True, null=True)
