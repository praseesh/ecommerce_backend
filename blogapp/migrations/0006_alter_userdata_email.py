# Generated by Django 5.1.2 on 2024-10-25 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0005_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='email',
            field=models.EmailField(max_length=100, unique=True),
        ),
    ]
