# Generated by Django 3.1 on 2020-08-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Carousel',
        ),
        migrations.DeleteModel(
            name='Link',
        ),
        migrations.AlterField(
            model_name='article',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='cover/%Y/%m/', verbose_name='文章图片'),
        ),
    ]
