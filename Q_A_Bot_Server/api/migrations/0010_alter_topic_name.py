# Generated by Django 4.0.6 on 2022-07-24 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_quiz_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
