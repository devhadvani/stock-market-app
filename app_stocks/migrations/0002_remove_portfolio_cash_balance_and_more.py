# Generated by Django 5.0.6 on 2024-05-13 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_stocks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='cash_balance',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='cash_balance',
            field=models.DecimalField(decimal_places=2, default=10000.0, max_digits=15),
        ),
    ]
