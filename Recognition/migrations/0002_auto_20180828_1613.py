# Generated by Django 2.1 on 2018-08-28 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recognition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagedatabase',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
