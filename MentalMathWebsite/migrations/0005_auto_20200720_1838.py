# Generated by Django 3.0.8 on 2020-07-21 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalMathWebsite', '0004_user_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='addition',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='division',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='multiplication',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='subtraction',
            field=models.IntegerField(default=0),
        ),
    ]
