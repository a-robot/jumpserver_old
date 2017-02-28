# coding=utf-8

from django.db import models


class Project(models.Model):
    project_name = models.CharField(max_length=100, verbose_name="项目名")

    def __str__(self):
        return self.project_name
