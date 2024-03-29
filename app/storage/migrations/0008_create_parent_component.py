# Generated by Django 4.1.4 on 2023-12-27 13:43

from django.db import migrations


class Migration(migrations.Migration):
    def create_parent_component(apps, schema_editor):
        ComponentType = apps.get_model("storage", "ComponentType")
        base_components = [
            "Плата АМ RX",
            "Плата АМ TX",
            "Плата АМ MDG RX",
            "Плата АМ MDG TX",
            "Плата РЧ RX",
            "Плата РЧ TX",
            "Плата РЧ MDG RX",
            "Плата РЧ MDG TX",
            #
            "Корпус АМ Плекс",
            "Корпус АМ Профиль",
            "Корпус АМ S Белый",
            "Корпус АМ S Серый",
            "Корпус АМ S Черный",
            "Корпус РЧ Плекс",
            "Корпус РЧ Профиль",
            "Корпус РЧ S Белый",
            "Корпус РЧ S Серый",
            "Корпус РЧ S Черный",
            #
            "БП АМ 1А",
            "БП АМ 2А",
            "БП РЧ 6А",
            "БП РЧ 3.2А",
            "Плата БП АМ",
        ]
        for component in base_components:
            ComponentType.objects.create(name=component)

    dependencies = [
        ("storage", "0007_alter_componenttype_options"),
    ]

    operations = [
        migrations.RunPython(create_parent_component),
    ]
