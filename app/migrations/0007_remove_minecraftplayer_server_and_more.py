# Generated by Django 5.1.7 on 2025-03-27 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_minecraftplayer_online_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="minecraftplayer",
            name="server",
        ),
        migrations.RemoveField(
            model_name="minecraftplayer",
            name="timestamp",
        ),
        migrations.AddField(
            model_name="minecraftplayer",
            name="ip",
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="minecraftplayer",
            name="play_time",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="minecraftplayer",
            name="online",
            field=models.BooleanField(),
        ),
    ]
