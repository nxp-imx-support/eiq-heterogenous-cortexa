# Generated by Django 2.1 on 2018-10-31 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recognition', '0010_imagedatabase_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagedatabase',
            name='voice_sample1',
            field=models.FileField(blank=True, default='', upload_to='samples/<name>'),
        ),
        migrations.AlterField(
            model_name='imagedatabase',
            name='voice_sample2',
            field=models.FileField(blank=True, default='', upload_to='samples/<name>'),
        ),
        migrations.AlterField(
            model_name='imagedatabase',
            name='voice_sample3',
            field=models.FileField(blank=True, default='', upload_to='samples/<name>'),
        ),
    ]