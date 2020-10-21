from django.db import models

# Create your models here.


from mdeditor.fields import MDTextField


# 轮播图
class Carousel(models.Model):
    img = models.ImageField('轮播图', upload_to='carousel/')
    url = models.URLField('图片链接', max_length=100)
    info = models.CharField('图片标题', max_length=50, default='')

    def __str__(self):
        return self.info

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'


# 友情链接
class Link(models.Model):
    logo = models.ImageField('网站图标', upload_to='logo/')
    name = models.CharField('链接名称', max_length=20)
    url = models.URLField('网址', max_length=100)
    describe = models.CharField('图片标题', max_length=50, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = '友情链接'


# 关于
class About(models.Model):
    body = MDTextField()
    time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '关于'
        verbose_name_plural = '关于'


# 网站配置
class WebsiteConfig(models.Model):
    name = models.CharField('网站名称', max_length=20)
    domain = models.URLField('网站域名', max_length=50)
    index_title = models.CharField('首页标题', max_length=50)
    keywords = models.CharField('META关键词', max_length=200)
    descript = models.CharField('META描述', max_length=300)
    copyright = models.CharField('版权信息', max_length=100)

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = '网站配置'


# 博主信息
class BloggerInfo(models.Model):
    position = models.CharField('职位', max_length=10)
    company = models.CharField('单位', max_length=20)
    location = models.CharField('地址', max_length=10)
    email = models.EmailField('邮箱', max_length=50)
    csdn = models.URLField('CSDN', max_length=50)
    github = models.URLField('GitHub', max_length=50)

    class Meta:
        verbose_name = '博主信息'
        verbose_name_plural = '博主信息'
