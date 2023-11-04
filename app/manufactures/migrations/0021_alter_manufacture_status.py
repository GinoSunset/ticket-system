# Generated by Django 4.1.4 on 2023-11-04 19:05

from django.db import migrations, models
import django.db.models.deletion
import manufactures.models


def set_default_for_manufacture_without_status(apps, schema_editor):
    Manufacture = apps.get_model("manufactures", "Manufacture")
    Dictionary = apps.get_model("additionally", "Dictionary")
    default_status = Dictionary.objects.get(
        code="new_manufacture_task", type_dict__code="status_manufactory"
    )
    Manufacture.objects.filter(status=None).update(status=default_status)
    print("set default status for manufacture without status")


class Migration(migrations.Migration):
    dependencies = [
        ("additionally", "0009_add_statuses_to_manuf_shipped"),
        ("manufactures", "0020_alter_nomenclature_amperage_1_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manufacture",
            name="status",
            field=models.ForeignKey(
                default=manufactures.models.get_default_new_manufacture_status,
                help_text="В ожидании, в работе ...",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="manufactures_status",
                to="additionally.dictionary",
                verbose_name="Статус",
            ),
        ),
        migrations.RunPython(set_default_for_manufacture_without_status),
    ]
