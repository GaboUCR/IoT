# Generated by Django 5.1.7 on 2025-06-15 02:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0008_alter_sensor_store_readings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=256)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('actuator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='sensors.actuator')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
