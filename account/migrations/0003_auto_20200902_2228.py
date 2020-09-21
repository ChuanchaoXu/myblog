# Generated by Django 3.1 on 2020-09-02 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20200902_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='web',
            field=models.URLField(blank=True, null=True, verbose_name='个人网站'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='sex',
            field=models.CharField(choices=[('1', '男'), ('2', '女')], default=1, max_length=1, verbose_name='性别'),
        ),
    ]
