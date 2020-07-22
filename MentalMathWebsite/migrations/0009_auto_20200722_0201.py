# Generated by Django 3.0.8 on 2020-07-22 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalMathWebsite', '0008_userprofilepicture_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofilepicture',
            name='image',
            field=models.URLField(default='', max_length=201),
        ),
    ]