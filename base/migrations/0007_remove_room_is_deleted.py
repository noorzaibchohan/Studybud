# Generated by Django 5.0.1 on 2024-04-24 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_message_options_room_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='is_deleted',
        ),
    ]