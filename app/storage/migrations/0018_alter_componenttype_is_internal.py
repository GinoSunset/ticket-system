# Generated by Django 4.1.4 on 2024-06-05 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0017_tagcomponent_componenttype_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="componenttype",
            name="is_internal",
            field=models.BooleanField(
                default=False,
                help_text="Если отмечено, то компонент будет отображаться в списке компонентов только для инженеров",
                verbose_name="Для внутреннего использования",
            ),
        ),
    ]