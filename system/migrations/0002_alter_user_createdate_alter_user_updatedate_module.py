# Generated by Django 4.0.3 on 2022-04-19 09:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='createDate',
            field=models.DateTimeField(db_column='create_date', default=datetime.datetime(2022, 4, 19, 9, 25, 47, 19850)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updateDate',
            field=models.DateTimeField(db_column='update_date', null=True),
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moduleName', models.CharField(db_column='module_name', max_length=50)),
                ('moduleStyle', models.CharField(db_column='module_style', max_length=120)),
                ('url', models.CharField(db_column='url', max_length=100)),
                ('parentOptValue', models.CharField(db_column='parent_opt_value', max_length=20)),
                ('grade', models.IntegerField(db_column='grade')),
                ('optValue', models.CharField(db_column='opt_value', max_length=20)),
                ('orders', models.IntegerField(db_column='orders')),
                ('isValid', models.IntegerField(db_column='is_valid', default=1)),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date', max_length=20)),
                ('parent', models.ForeignKey(db_column='parent_id', db_constraint=False, default=-1, on_delete=django.db.models.deletion.DO_NOTHING, to='system.module')),
            ],
            options={
                'db_table': 't_module',
            },
        ),
    ]