# Generated by Django 4.2.4 on 2023-08-10 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_userwallet_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userwallet',
            name='disanled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]