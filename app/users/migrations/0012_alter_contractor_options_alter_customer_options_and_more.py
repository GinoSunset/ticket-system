# Generated by Django 4.1.4 on 2023-04-12 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0011_alter_user_phone"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contractor",
            options={
                "verbose_name": "Исполнитель",
                "verbose_name_plural": "Исполнители",
            },
        ),
        migrations.AlterModelOptions(
            name="customer",
            options={"verbose_name": "Заказчик", "verbose_name_plural": "Заказчики"},
        ),
        migrations.AlterModelOptions(
            name="customerprofile",
            options={
                "verbose_name": "Профиль заказчика",
                "verbose_name_plural": "Профили заказчиков",
            },
        ),
        migrations.AlterModelOptions(
            name="operator",
            options={"verbose_name": "Оператор", "verbose_name_plural": "Операторы"},
        ),
        migrations.AlterField(
            model_name="customerprofile",
            name="linked_operators",
            field=models.ManyToManyField(
                blank=True,
                help_text="Какие операторы могут работать с этим заказчиком",
                null=True,
                related_name="customers",
                to="users.operator",
                verbose_name="Операторы заказчика",
            ),
        ),
    ]
