# Generated by Django 4.1.4 on 2023-12-28 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0008_create_parent_component"),
    ]

    operations = [
        migrations.AddField(
            model_name="component",
            name="is_archive",
            field=models.BooleanField(default=False, verbose_name="В архиве"),
        ),
    ]
