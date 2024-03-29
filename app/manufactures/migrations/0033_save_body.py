# Generated by Django 4.1.4 on 2023-12-26 17:42

from django.db import migrations


class Migration(migrations.Migration):
    def save_body_from_body_option(apps, schema_editor):
        Nomenclature = apps.get_model("manufactures", "Nomenclature")
        BodyOption = apps.get_model("manufactures", "BodyOption")
        bodies = [
            ["PL", "Плекс"],
            ["PR", "Профиль"],
            ["SW", "S Белый"],
            ["SG", "S Серый"],
            ["SB", "S Черный"],
        ]
        for type_, body in bodies:
            body_option, _ = BodyOption.objects.get_or_create(name=body)
            print(f"BodyOption: {body} created")
            nomenclatures = Nomenclature.objects.filter(body_option=type_)
            print(f"Found {nomenclatures.count()} nomenclatures")
            for nomenclature in nomenclatures:
                print(f"Update nomenclature {nomenclature}")
                nomenclature.body = body_option
                nomenclature.save()

    dependencies = [
        ("manufactures", "0032_nomenclature_body"),
    ]

    operations = [migrations.RunPython(save_body_from_body_option)]
