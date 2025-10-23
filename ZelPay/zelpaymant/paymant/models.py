from django.db import models
from django.conf import settings
from zelpaymant.common.models import BaseModel 

class TransactionPayload(BaseModel):
    payment_status = models.CharField(
        max_length=50,
        choices=[("pending", "در انتظار"), ("paid", "پرداخت شده"), ("failed", "ناموفق")],
        default="pending"
    )
    payment_gateway = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    payment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    server_id_process = models.GenericIPAddressField()

    transaction_data = models.JSONField()

    token_url = models.CharField(max_length=144)

    is_verified = models.BooleanField(default=False)

    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, null=True, blank=True)
    
class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_interactions")
    destination = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_interactions")
    authority = models.CharField(max_length=144)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    is_valid = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    callback_url = models.URLField()
    idempotency_key = models.UUIDField(null=False)
    token = models.CharField(max_length=64, unique=True, editable=False)  # هش ذخیره میشه    # TODO: add network field in another table
    def save(self,*args,**kwargs):
        assert self.token , "Dont Validate Token"
        return super().save(*args,**kwargs)



""" # check the iu
BEGAN TRANAMACTION 
INSERT  INTO Transaction values (
authority , 
amount,
balance_after,
is_valid,
is_completed,
callback_url
)
"""