# Generated by Django 5.0.4 on 2024-04-19 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excerpt', '0055_alter_excerpt_created_at_alter_excerpt_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excerpt',
            name='created_at',
            field=models.DateTimeField(default='2024-04-19 11:43:39.423031'),
        ),
        migrations.AlterField(
            model_name='excerpt',
            name='updated_at',
            field=models.DateTimeField(default='2024-04-19 11:43:39.423250'),
        ),
    ]
