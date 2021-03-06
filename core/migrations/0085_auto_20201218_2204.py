# Generated by Django 2.2.14 on 2020-12-18 16:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0084_subcription_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name_plural': 'Product Comments'},
        ),
        migrations.AlterModelOptions(
            name='homeimage',
            options={'verbose_name_plural': 'Banner'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name_plural': 'Orders Details'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name_plural': 'Product Payments'},
        ),
        migrations.AlterModelOptions(
            name='subcription',
            options={'verbose_name_plural': 'Subscription Plans'},
        ),
        migrations.RemoveField(
            model_name='billingaddress',
            name='address',
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='address_type',
            field=models.CharField(blank=True, choices=[('B', 'Billing')], max_length=1),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Email Id'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='fname',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='lname',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Item Name'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='seller_msg',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Reason'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tax',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Service Charges'),
        ),
        migrations.CreateModel(
            name='SubscriptionPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Subscription Payments',
            },
        ),
    ]
