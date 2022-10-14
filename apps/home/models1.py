# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from unittest.util import _MAX_LENGTH
from xml.parsers.expat import model
from django.db import models
from django.contrib.auth.models import User
import jsonfield

import uuid
import pathlib

from apps.home import relevant_statues

# from judgment_prediction.apps.home.similar_cases import similarcase

# Create your models here.

class Case(models.Model):
    case_name=models.CharField(max_length=120)
    case_description=models.TextField(max_length=100,default=True)
    case_status=models.CharField(max_length=40,default=True)
    hash_key=models.CharField(max_length=40,default=False)
    transaction_id=models.CharField(max_length=40,default=False)
    similarcases = jsonfield.JSONField()
    relevant_statues = jsonfield.JSONField()


    def __str__(self):
        return self.case_name

    
class Todo(models.Model):
    text = models.CharField(max_length=40)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Statutes(models.Model):
    sec_name=models.CharField(max_length=50)
    sec_title=models.CharField(max_length=50)
    sec_def=models.TextField(max_length=100,default=True)

    def __str__(self):
        return self.sec_name

class Sec(models.Model):
    sec_name=models.CharField(max_length=50)
    sec_def=models.TextField(max_length=100,default=True)

    def __str__(self):
        return self.sec_name


def upload_handler(instance, filename):
    fpath = pathlib.Path(filename)
    new_name = str(uuid.uuid1())
    return  f"media/{new_name}{fpath.suffix}"



class UploadCaseFile(models.Model):
    uploadfile_name = models.CharField(default=None, max_length=50)
    uploadfile_short_desc =  models.TextField(default="", blank=True,null=True)
    uploadfile_description = models.TextField(default="", blank=True,null=True)
    uploadfile = models.FileField(upload_to='new_cases/',null=True,blank=True)
    prediction = models.CharField(default="None",blank=True,null=True,max_length=50)

    def __str__(self):
        return self.uploadfile_name
