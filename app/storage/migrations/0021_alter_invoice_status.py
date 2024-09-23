# Generated by Django 5.1 on 2024-09-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0020_alter_delivery_status_alter_invoice_delivery"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="status",
            field=models.IntegerField(
                choices=[
                    (5, "Новый"),
                    (10, "В работе"),
                    (20, "Обработан"),
                    (100, "Ошибка"),
                ],
                default=5,
                verbose_name="Статус",
            ),
        ),
    ]