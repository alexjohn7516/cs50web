# Generated by Django 3.2.8 on 2021-11-08 22:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 8, 22, 3, 24, 768749)),
        ),
    ]