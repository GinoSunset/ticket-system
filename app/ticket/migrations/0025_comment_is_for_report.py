# Generated by Django 4.1.4 on 2023-02-20 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0024_alter_ticket_completion_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="is_for_report",
            field=models.BooleanField(default=False),
        ),
    ]