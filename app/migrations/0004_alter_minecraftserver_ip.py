# Generated by Django 5.1.7 on 2025-03-27 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_minecraftserver_ip"),
    ]

    operations = [
        migrations.AlterField(
            model_name="minecraftserver",
            name="ip",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
