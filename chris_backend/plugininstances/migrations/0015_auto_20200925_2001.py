# Generated by Django 2.2.12 on 2020-09-26 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugininstances', '0014_auto_20200610_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugininstance',
            name='status',
            field=models.CharField(choices=[('created', 'Default initial'), ('waitingForPrevious', 'Waiting for previous to finish'), ('scheduled', 'Scheduled to the worker'), ('started', 'Sent to remote compute'), ('finishedSuccessfully', 'Finished successfully'), ('finishedWithError', 'Finished with error'), ('cancelled', 'Cancelled')], default='created', max_length=30),
        ),
    ]
