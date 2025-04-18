# Generated by Django 4.2.4 on 2025-03-15 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_alter_order_paid_amount_alter_order_shipping_cost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='product_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total cost exclude shipping cost', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='product_amount_bf_tax',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total cost exclude shipping cost & before tax', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
