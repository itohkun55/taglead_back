# Generated by Django 3.2.5 on 2021-10-28 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_memomainbackup_typebackupcase'),
    ]

    operations = [
        migrations.AddField(
            model_name='memomain',
            name='boolHasDelete',
            field=models.BooleanField(default=False, verbose_name='削除済みフラグ'),
        ),
    ]
