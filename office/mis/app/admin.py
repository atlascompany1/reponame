
from django.contrib import admin
from .models import Account, Transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'account_type', 'balance_af', 'balance_usd',
        'available_af', 'available_usd',
        'total_deposit_af', 'total_deposit_usd',
        'total_withdraw_af', 'total_withdraw_usd',
        'status', 'manager'
    )
    search_fields = ('name', 'account_type', 'manager')
    list_filter = ('account_type', 'status')
    inlines = [TransactionInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'type', 'amount_af', 'amount_usd', 'date')
    list_filter = ('type', 'date')
    search_fields = ('account__name', 'description')

