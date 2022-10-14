# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
from .models import Case
admin.site.register(Case)

from .models import Todo
admin.site.register(Todo)

from .models import Statutes
admin.site.register(Statutes)

from .models import UploadCaseFile
admin.site.register(UploadCaseFile)

from .models import UploadHearingFile
admin.site.register(UploadHearingFile)


from .models import UploadHearingFile1
admin.site.register(UploadHearingFile1)
