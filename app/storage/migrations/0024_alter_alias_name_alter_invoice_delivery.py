# Generated by Django 5.1 on 2024-09-15 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0023_invoicealiasrelation_invoice_alias"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alias",
            name="name",
            field=models.CharField(max_length=255, unique=True, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="delivery",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="storage.delivery",
                verbose_name="Доставка",
            ),
        ),
    ]