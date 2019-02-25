# Generated by Django 2.1.5 on 2019-02-20 15:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('face_detector', '0008_auto_20190220_1146'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='similarity',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='person',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата'),
            preserve_default=False,
        ),
    ]
