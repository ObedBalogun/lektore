from django.db import models
from django.contrib.auth.models import User

from app.commons import USER_CATEGORY, TRANSACTION_TYPE, TRANSACTION_CATEGORY
from app.shared_models import Timestamp
from django.contrib.postgres.indexes import BrinIndex


class Wallet(Timestamp):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="user_wallet")
    # TODO: Use IntegerField instead?!
    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=19)
    user_category = models.CharField(max_length=10, choices=USER_CATEGORY)
    provider = models.CharField(max_length=150)

    def __str__(self):
        return self.user.username

    def credit_wallet(self, amount, kobo=False):
        if not amount or amount == 0:
            return False
        try:
            if kobo:
                self.balance = int(self.balance) + amount/100
            else:
                self.balance = int(self.balance) + amount
            self.save()
        except ValueError:
            return False
        return True

    def debit_wallet(self, amount, kobo=False):
        if not amount or amount == 0:
            return False
        try:
            if kobo:
                amount = amount / 100
            if amount > self.balance:
                return False
            self.balance = self.balance - amount
            self.save()
        except ValueError:
            return False
        return True


class WalletTransaction(Timestamp):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="wallet_transaction")
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=19)
    destination = models.CharField(max_length=250)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    transaction_category = models.CharField(max_length=200, choices=TRANSACTION_CATEGORY)
    payment_status = models.BooleanField(default=False)
    reference = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        indexes = (
            BrinIndex(fields=['created']),
        )
