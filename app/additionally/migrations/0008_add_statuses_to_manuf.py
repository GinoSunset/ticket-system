# Generated by Django 4.1.4 on 2023-06-03 08:56

from django.db import migrations


def add_manufactory_statuses(apps, schema_editor):
    DictionaryType = apps.get_model("additionally", "DictionaryType")
    Dictionary = apps.get_model("additionally", "Dictionary")
    status_type = DictionaryType.objects.create(
        code="status_manufactory", description="Словарь статусов для производства"
    )
    status_codes = [
        ("new_manufacture_task", "Новая"),
        ("in_progress", "В работе"),
        ("ready", "Готова"),
        ("canceled", "Отменена"),
    ]
    for code, description in status_codes:
        Dictionary.objects.create(
            type_dict=status_type, code=code, description=description
        )


class Migration(migrations.Migration):
    dependencies = [
        ("additionally", "0007_add_status_cancel"),
    ]

    operations = [
        migrations.RunPython(add_manufactory_statuses),
    ]
