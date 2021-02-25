# Generated by Django 2.2.4 on 2020-08-07 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20200806_1830'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='variationname',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='variationname',
            name='product',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Variation'),
        ),
        migrations.DeleteModel(
            name='ProductVariation',
        ),
        migrations.DeleteModel(
            name='VariationName',
        ),
    ]
