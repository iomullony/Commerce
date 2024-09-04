# Generated by Django 5.0.1 on 2024-09-04 09:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auction_winner_alter_auction_seller_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_comments', to='auctions.auction'),
        ),
    ]
