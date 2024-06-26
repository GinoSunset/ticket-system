# Generated by Django 4.1.4 on 2024-05-27 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0016_alter_delivery_options_remove_delivery_components_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TagComponent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, unique=True, verbose_name="Тег"),
                ),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.AddField(
            model_name="componenttype",
            name="tags",
            field=models.ManyToManyField(to="storage.tagcomponent"),
        ),
    ]
