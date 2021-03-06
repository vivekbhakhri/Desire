# Generated by Django 2.2.14 on 2020-10-24 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_auto_20201024_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='unique_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='ref_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Reference ID'),
        ),
    ]
