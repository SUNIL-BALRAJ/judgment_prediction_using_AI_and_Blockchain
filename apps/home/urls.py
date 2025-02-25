# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

from django.conf import settings #add this
from django.conf.urls.static import static


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('adddb', views.addCasetoDB, name='adddb'),
    path('sec', views.sec, name='sec'),
    path('analysis', views.case_analysis, name='analysis'),
    path('trans', views.translate, name='trans'),
    path('all_cases', views.all_cases, name='all_cases'),
    # path('uploaded_cases', views.uploaded_cases, name='uploaded_cases'),
    # path('similar_case_retrieval', views.similar_case_retrieval, name='similar_case_retrieval'),
    path('petitioner', views.petitioner, name='petitioner'),
    path('relevant_statue_retrieval', views.relevant_statue_retrieval, name='relevant_statue_retrieval'),
    path('hearing_home', views.hearing_upload, name='hearing_home'),
    path('virtual_courtroom', views.get_virtual_courtroom, name='virtual_courtroom'),
    path('case_status_flow', views.get_status_flow, name='case_status_flow'),
    re_path('allocate_judges/(?P<id>[\w-]+)/$',views.allocate_judges, name='allocate_judges'),

    re_path('view_case/(?P<id>[\w-]+)/$', views.view_case, name='view_case'),
    re_path('similar/(?P<id>[\w-]+)/$', views.get_similar_cases, name='similar'),
    re_path('all_analysis/(?P<id>[\w-]+)/$', views.get_query_analysis, name='all_analysis'),
    re_path('statues/(?P<id>[\w-]+)/$',views.get_relevant_statues, name='statues'),
    
   
    #path('analysis/',views.analysis),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
    
] 
