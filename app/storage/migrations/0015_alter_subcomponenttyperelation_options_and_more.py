# Generated by Django 4.1.4 on 2024-01-11 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0014_componenttype_parent_component_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subcomponenttyperelation",
            options={
                "verbose_name": "Связь типов компонентов",
                "verbose_name_plural": "Связь типов компонентов",
            },
        ),
        migrations.RemoveField(
            model_name="componenttype",
            name="parent_component_type",
        ),
        migrations.AddField(
            model_name="componenttype",
            name="sub_components_type",
            field=models.ManyToManyField(
                related_name="parent_component_type",
                through="storage.SubComponentTypeRelation",
                to="storage.componenttype",
                verbose_name="Тип подкомпонента",
            ),
        ),
    ]
