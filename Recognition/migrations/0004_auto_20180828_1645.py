# Generated by Django 2.1 on 2018-08-28 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recognition', '0003_auto_20180828_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagedatabase',
            name='face',
            field=models.ImageField(default='', upload_to='C:\\Users\\nxf45231\\Desktop\\Stuff\\SmartDoor\\static\\detection'),
        ),
    ]
