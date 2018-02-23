# Generated by Django 2.0.2 on 2018-02-22 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Userdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(max_length=255)),
                ('songid', models.CharField(max_length=255)),
                ('heartrate', models.IntegerField()),
                ('rating', models.FloatField()),
                ('time', models.IntegerField(default=1072)),
            ],
        ),
    ]