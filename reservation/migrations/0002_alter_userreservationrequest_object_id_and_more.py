# Generated by Django 5.1.2 on 2024-10-23 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreservationrequest',
            name='object_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='userreservationreturn',
            name='object_id',
            field=models.CharField(max_length=100),
        ),
    ]
