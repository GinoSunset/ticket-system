# Generated by Django 4.1.4 on 2023-12-26 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0006_remove_componenttype_parent_component_type_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="componenttype",
            options={
                "verbose_name": "Тип компонента",
                "verbose_name_plural": "Типы компонентов",
            },
        ),
    ]