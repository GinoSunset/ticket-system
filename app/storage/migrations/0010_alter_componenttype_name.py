# Generated by Django 4.1.4 on 2023-12-29 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0009_component_is_archive"),
    ]

    operations = [
        migrations.AlterField(
            model_name="componenttype",
            name="name",
            field=models.CharField(
                max_length=255, unique=True, verbose_name="Название типа компонента"
            ),
        ),
    ]
