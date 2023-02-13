# Generated by Django 4.1.4 on 2023-02-13 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_user_email_notify_user_telegram_notify"),
        ("ticket", "0021_alter_comment_options_alter_commentfile_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="responsible",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="users.operator",
                verbose_name="Ответственный",
            ),
        ),
    ]