# Generated by Django 4.2.4 on 2023-08-10 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("theatre", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="play",
            name="actors",
            field=models.ManyToManyField(blank=True, to="theatre.actor"),
        ),
        migrations.AddField(
            model_name="play",
            name="genres",
            field=models.ManyToManyField(blank=True, to="theatre.genre"),
        ),
        migrations.AddField(
            model_name="performance",
            name="play",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="theatre.play"
            ),
        ),
        migrations.AddField(
            model_name="performance",
            name="theatre_hall",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="theatre.theatrehall"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("performance", "row", "seat")},
        ),
    ]
