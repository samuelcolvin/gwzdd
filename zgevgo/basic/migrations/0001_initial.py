# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import zgevgo.basic.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('self_sha', zgevgo.basic.models.ShaField(unique=True, max_length=40, editable=False, db_index=True)),
                ('parent_sha', zgevgo.basic.models.ShaField(unique=True, max_length=40, editable=False, db_index=True)),
                ('timestamp', models.DateTimeField()),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='action',
            name='author',
            field=models.ForeignKey(to='basic.Author'),
        ),
        migrations.AddField(
            model_name='action',
            name='stream',
            field=models.ForeignKey(to='basic.Stream'),
        ),
    ]
