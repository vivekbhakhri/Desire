# Generated by Django 2.2.4 on 2020-08-05 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_productvariation'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariation',
            name='category',
            field=models.CharField(choices=[('size', 'size'), ('color', 'color')], default=None, max_length=100),
        ),
    ]
