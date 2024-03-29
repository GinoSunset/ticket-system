# Generated by Django 4.1.4 on 2023-12-26 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0030_alter_nomenclature_frame_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="BodyOption",
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
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "description",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
            ],
        ),
        migrations.RenameField(
            model_name="nomenclature",
            old_name="body",
            new_name="body_option",
        ),
    ]
