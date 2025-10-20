from django.db import models
from django.conf import settings
from zelpaymant.common.models import BaseModel, MixinFaceCheck, MixinPaymentFaceCheck

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TokenAbsractionModel(models.Model):
    token = models.CharField(max_length=122, editable=False, null=False)

    class Meta:
        abstract = True


class WalletAbstractBaseModel(models.Model):
    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    category = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Wallet(TokenAbsractionModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    secret_key = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.user})"

class Transaction(WalletAbstractBaseModel, MixinPaymentFaceCheck, TokenAbsractionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    from_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_from")
    factor = models.ForeignKey('Invoice', on_delete=models.DO_NOTHING, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="transactions")

    def __str__(self):
        return f"Transaction {self.id} - {self.user}"


class Expense(Transaction):
    pass


class Income(Transaction):
    pass


class Invoice(BaseModel):
    class Status(models.IntegerChoices):
        draft = 0, 'draft'
        issued = 1, 'issued'
        paid = 2, 'paid'
        cancelled = 3, 'cancelled'

    invoice_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.user}"
