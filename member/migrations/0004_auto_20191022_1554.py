# Generated by Django 2.0 on 2019-10-22 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0003_auto_20191022_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='birth_day',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='member',
            name='birth_month',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='member',
            name='birth_year',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='member',
            name='remain_points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
