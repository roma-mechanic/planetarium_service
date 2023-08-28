# Generated by Django 4.2.4 on 2023-08-26 20:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("planetarium", "0008_alter_planetariumdome_website"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="astronomyshow",
            options={},
        ),
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ["show_session", "reservation"]},
        ),
        migrations.AlterField(
            model_name="reservation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]