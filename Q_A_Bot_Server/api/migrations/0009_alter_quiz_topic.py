# Generated by Django 4.0.6 on 2022-07-24 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_quiz_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz', to='api.topic'),
        ),
    ]
