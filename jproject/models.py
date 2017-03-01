# coding=utf-8

from django.db import models


class Project(models.Model):
    project_name = models.CharField(max_length=100, verbose_name='项目名')

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = verbose_name


class AppModule(models.Model):
    project = models.ForeignKey(Project, verbose_name='所属项目')
    app_module_name = models.CharField(max_length=100, verbose_name='应用模块')

    def __str__(self):
        return '%s-%s' % (self.project, self.app_module_name)

    class Meta:
        verbose_name = "应用模块"
        verbose_name_plural = verbose_name
