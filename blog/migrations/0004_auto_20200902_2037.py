# Generated by Django 3.1 on 2020-09-02 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_article_recommend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='recommend',
            field=models.BooleanField(default=False, verbose_name='推荐显示'),
        ),
    ]
