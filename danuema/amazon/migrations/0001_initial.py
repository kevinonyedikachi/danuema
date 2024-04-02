# Generated by Django 5.0.3 on 2024-03-13 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Amazon_Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_sku', models.CharField(max_length=100)),
                ('amazon_order_id', models.CharField(max_length=100)),
                ('order_item_id', models.CharField(max_length=100)),
                ('quantity_ordered', models.IntegerField()),
                ('purchase_date', models.DateTimeField()),
                ('unshipped', models.BooleanField(default=True)),
            ],
        ),
    ]