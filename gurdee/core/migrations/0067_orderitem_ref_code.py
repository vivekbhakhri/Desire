# Generated by Django 2.2.4 on 2020-10-15 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20201015_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='ref_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
