# Generated by Django 5.0.4 on 2024-04-21 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excerpt', '0064_alter_excerpt_created_at_alter_excerpt_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excerpt',
            name='created_at',
            field=models.DateTimeField(default='2024-04-21 08:57:33.855560'),
        ),
        migrations.AlterField(
            model_name='excerpt',
            name='updated_at',
            field=models.DateTimeField(default='2024-04-21 08:57:33.855601'),
        ),
    ]
