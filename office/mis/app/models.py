from django.db import models
from django.utils import timezone
from django.db.models import Sum

class Account(models.Model):
    TYPE_CHOICES = (
        ('Exchange', 'صرافی'),
        ('Tank', 'تانک تیل'),
    )

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    manager = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # فیلدهای محاسبه شده (Auto-update)
    balance_af = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    available_af = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    available_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deposit_af = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deposit_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_withdraw_af = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_withdraw_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.account_type})"

    def update_balances(self):
        deposits = self.transactions.filter(type='deposit').aggregate(
            total_af=Sum('amount_af'), total_usd=Sum('amount_usd'))
        withdrawals = self.transactions.filter(type='withdrawal').aggregate(
            total_af=Sum('amount_af'), total_usd=Sum('amount_usd'))

        self.total_deposit_af = deposits['total_af'] or 0
        self.total_deposit_usd = deposits['total_usd'] or 0
        self.total_withdraw_af = withdrawals['total_af'] or 0
        self.total_withdraw_usd = withdrawals['total_usd'] or 0

        self.balance_af = self.total_deposit_af - self.total_withdraw_af
        self.balance_usd = self.total_deposit_usd - self.total_withdraw_usd
        self.available_af = self.balance_af  # می‌توان قوانین برداشت اضافه کرد
        self.available_usd = self.balance_usd
        self.save()


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('deposit', 'واریز'),
        ('withdrawal', 'برداشت'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount_af = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.account.update_balances()  # آپدیت اتوماتیک بعد از هر تراکنش

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.account.update_balances()  # آپدیت اتوماتیک بعد از حذف تراکنش


