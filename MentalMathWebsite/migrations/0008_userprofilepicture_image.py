# Generated by Django 3.0.8 on 2020-07-21 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalMathWebsite', '0007_userprofilepicture'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilepicture',
            name='image',
            field=models.URLField(default=''),
        ),
    ]
