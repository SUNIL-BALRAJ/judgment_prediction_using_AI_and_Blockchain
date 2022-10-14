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


choices =  [
    ('Criminal Matters',"Criminal Matters"),
    ('Land Acquisition', 'Land Acquisition'),
    ('Labour Matters', 'Labour Matters'),
    ('Family courts',"Family courts"),
    ('Petty Cases',"Petty Cases")
]

class UploadCaseFile(models.Model):
    uploadfile_name = models.CharField(default=None, max_length=50)
    uploadfile_short_desc =  models.TextField(default="", blank=True,null=True)
    uploadfile_description = models.TextField(default="", blank=True,null=True)
    uploadfile = models.FileField(upload_to='new_cases/',null=True,blank=True)
    prediction = models.CharField(default="None",blank=True,null=True,max_length=50)
    category =  models.CharField(max_length=24, choices=choices, default='None')
    date_filed = models.CharField(max_length=50,blank=True,null=True, default='None')
    court = models.CharField(max_length=50,blank=True,null=True, default='None')
    judge = models.CharField(max_length=50,blank=True,null=True, default='None')
    num_hearings = models.CharField(max_length=50,blank=True,null=True, default='None')
    priority = models.CharField(max_length=50,blank=True,null=True, default='None')
    
    

    def __str__(self):
        return self.uploadfile_name

class UploadHearingFile(models.Model):
    h_uploadfile_name = models.CharField(default=None, max_length=50)
    h_uploadfile = models.FileField(upload_to='new_hearings/',null=True,blank=True)
    h_hash = models.TextField(default="", blank=True,null=True)

    def __str__(self):
        return self.h_uploadfile_name


class UploadHearingFile1(models.Model):
    h_uploadfile_name = models.CharField(default=None, max_length=50)
    h_uploadfile = models.FileField(upload_to='new_hearings/',null=True,blank=True)
    h_hash = models.TextField(default="", blank=True,null=True)

    def __str__(self):
        return self.h_uploadfile_name

