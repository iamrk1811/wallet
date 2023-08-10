# Generated by Django 4.2.4 on 2023-08-10 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_idempotenttable'),
    ]

    operations = [
        migrations.AddField(
            model_name='idempotenttable',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'deposit'), (2, 'withdraw')], null=True),
        ),
    ]