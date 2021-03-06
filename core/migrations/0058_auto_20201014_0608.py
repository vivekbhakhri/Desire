# Generated by Django 2.2.4 on 2020-10-14 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20201013_0554'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='fname',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='lname',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='address_type',
            field=models.CharField(blank=True, choices=[('B', 'Billing'), ('S', 'Shipping')], max_length=1),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='apartment_address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='country',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='street_address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='zip',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
