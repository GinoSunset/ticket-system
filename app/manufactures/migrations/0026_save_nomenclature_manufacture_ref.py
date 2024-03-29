# Generated by Django 4.1.4 on 2023-11-07 18:40

from django.db import migrations


def save_nomenclature_manufacture_ref(apps, schema_editor):
    Nomenclature = apps.get_model("manufactures", "Nomenclature")
    for nomenclature in Nomenclature.objects.all():
        nomenclature._manufactures = nomenclature.manufactures.all().first()
        nomenclature.save()


def save_manufacture_nomenclature_ref_to_m2m(apps, schema_editor):
    # Reverse operation of save_nomenclature_manufacture_ref
    Nomenclature = apps.get_model("manufactures", "Nomenclature")
    for nomenclature in Nomenclature.objects.all():
        if nomenclature._manufactures:
            nomenclature.manufactures.add(nomenclature._manufactures)


class Migration(migrations.Migration):
    dependencies = [
        ("manufactures", "0025_nomenclature__manufactures"),
    ]

    operations = [
        migrations.RunPython(
            save_nomenclature_manufacture_ref,
            save_manufacture_nomenclature_ref_to_m2m,
        ),
    ]
