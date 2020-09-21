# Generated by Django 3.1 on 2020-09-02 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userinfo',
            options={'verbose_name': '用户详细信息', 'verbose_name_plural': '用户详细信息'},
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photo/%Y/%m/', verbose_name='头像'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='sex',
            field=models.CharField(choices=[('1', '男'), ('2', '女')], default=0, max_length=1, verbose_name='性别'),
        ),
    ]
