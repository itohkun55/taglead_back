# Generated by Django 3.2.5 on 2021-10-14 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210924_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='memomain',
            name='boolHasModified',
            field=models.BooleanField(blank=True, default=False, verbose_name='修正済みフラグ'),
        ),
    ]