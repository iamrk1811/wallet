# Generated by Django 4.2.4 on 2023-08-10 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdempotentTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_id', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]