from app.shared_models import Timestamp
from django.contrib.auth.models import User
from django.db import models


class Transaction(Timestamp):
    TRANSACTION_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit')
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_transactions")
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=19)
    reference = models.CharField(max_length=255)
    service_provider = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=200, choices=TRANSACTION_TYPES, default='debit')
    status = models.BooleanField(default=False)
