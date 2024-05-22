from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    
class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)

class Order(models.Model):
    ORDER_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Additional fields such as order status, order type (market, limit, etc.)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=11, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Additional fields such as transaction status, transaction fees, etc.

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ManyToManyField(Stock)
    # Additional fields such as watchlist name, etc.

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # Additional fields such as notification type, etc.

# Additional models can be added for features like dividends, corporate actions, historical data, etc.
