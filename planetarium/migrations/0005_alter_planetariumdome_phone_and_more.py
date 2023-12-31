# Generated by Django 4.2.4 on 2023-08-20 15:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("planetarium", "0004_remove_planetariumdome_dome_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planetariumdome",
            name="phone",
            field=models.CharField(blank=True, max_length=63, null=True),
        ),
        migrations.AlterField(
            model_name="planetariumdome",
            name="website",
            field=models.URLField(blank=True, null=True),
        ),
    ]
