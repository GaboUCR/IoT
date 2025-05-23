# Generated by Django 5.1.7 on 2025-04-28 18:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('sensor_type', models.CharField(max_length=32)),
                ('unit', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='SensorReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='readings', to='sensors.sensor')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['timestamp'], name='sensors_sen_timesta_8162d3_idx'), models.Index(fields=['sensor'], name='sensors_sen_sensor__113d40_idx')],
            },
        ),
    ]
