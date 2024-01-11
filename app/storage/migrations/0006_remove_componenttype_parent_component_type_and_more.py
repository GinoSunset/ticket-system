# Generated by Django 4.1.4 on 2023-12-24 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0005_alter_component_options_remove_component_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="componenttype",
            name="parent_component_type",
        ),
        migrations.AddField(
            model_name="componenttype",
            name="parent_component_type",
            field=models.ManyToManyField(
                help_text="Выберите тип компонента, в состав которого входит данный компонент",
                related_name="sub_components_type",
                to="storage.componenttype",
                verbose_name="Тип родительского подкомпонента",
            ),
        ),
    ]