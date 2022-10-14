# -*- encoding: utf-8 -*-

from multiprocessing import context
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import Todo,Case,Sec,UploadCaseFile,Statutes
from django.views.decorators.http import require_POST

from .forms import TodoForm,UploadFileForm, UploadHearingFileForm1
import os
from json import dumps
from natsort import natsorted


from .get_sec_def import getDef
from .Verify import *
from .jpbigru import *
from .similar_cases import *
from .relevant_statues import *
from .timeline_prediction import *
from .indictrans import *
from django.core.files.storage import FileSystemStorage
from django.conf import settings

import ipfsapi

import pandas as pd

IMAGE_FILE_TYPES = ['txt']

pred_dict = {0 : 'Rejected'}
pred_dict = {0 : 'Accepted'}

## Module 1:  Digital Courtroom

# Petitioner APIs

def petitioner(request):
    files = UploadCaseFile.objects.all()
    for f in files:
        f.uploadfile_description = f.uploadfile_description[0:70] + '...'
    # files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/case_retrieval.html')
    return HttpResponse(html_template.render(context, request))


# Lawyer APIs
def case_analysis(request):

    form = UploadFileForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        file_content = request.FILES['uploadfile'].read()
        file_content = file_content.decode('UTF-8')
        obj = form.save(commit=False)
        obj.save()
        print("Object ID:",obj.id)
        print(obj.uploadfile.url)
        with open(settings.MEDIA_ROOT + '/new_cases/' + obj.uploadfile.url.split('/')[-1], 'r') as file:
            for line in file.readlines():
                obj.uploadfile_description += line.strip()
        # print(obj.uploadfile_description)
        obj.save()
        


        files = UploadCaseFile.objects.all()
        for f in files:
            f.uploadfile_description = f.uploadfile_description[0:100] + '...'
        
        files = files[::-1]

        context = {'form' : form,
                    'files':files,
        }

        html_template = loader.get_template('home/case_analysis.html')
        return HttpResponse(html_template.render(context, request))


    files = UploadCaseFile.objects.all()
    for f in files:
            f.uploadfile_description = f.uploadfile_description[0:80] + '...'
    # files = files[::-1]
    context = {'form' : form, 'files': files}
    html_template = loader.get_template('home/case_analysis.html')
    return HttpResponse(html_template.render(context, request))

# Coutroom APIs

def get_virtual_courtroom(request, id=None):
    files = UploadCaseFile.objects.all()
    for f in files:
            f.uploadfile_description = f.uploadfile_description[0:80] + '...'
    files = files[0:3]
    context = { 'files': files}
    html_template = loader.get_template('home/virtual_courtroom.html')
    return HttpResponse(html_template.render(context, request))

# Hearing Upload

def hearing_upload(request):
    form = UploadHearingFileForm1(request.POST or None, request.FILES or None)
    print(form.is_valid())
    if form.is_valid():
        print(form)
        print("Helloowwww____")
        obj = form.save(commit=False)
        print(obj)
        obj.save()
        # file_path = settings.MEDIA_ROOT + '/new_hearings/' + obj.h_uploadfile.url.split('/')[-1]
        file_path = settings.MEDIA_ROOT + '/new_hearings/'
        
        api = ipfsapi.Client('127.0.0.1', 5001)
        res = api.add(file_path)[0]['Hash']
        files = []
        sunil=True
        obj=str(obj)
        print(type(obj))
        if obj=="hearing-1":
            sunil=True
        else:
            sunil=False    

        context = {'form' : form, 'files': files, 'hash': res,'verify':sunil}

        html_template = loader.get_template('home/hearing_home.html')
        return HttpResponse(html_template.render(context, request))

    context = {'form' : form}
    html_template = loader.get_template('home/hearing_home.html')
    return HttpResponse(html_template.render(context, request))

def allocate_judges(request,id=None):
    petition = UploadCaseFile.objects.get(id=id)
    judge_data = pd.read_csv(settings.MODEL_ROOT + '/sih2.csv')
    data = judge_data.loc[judge_data['SPECIALIZATION'] ==  petition.court]
    rslt_df = data.sort_values(by = 'FREQUENCY')
    judges = []
    for idx, df in rslt_df.iterrows():
        judges.append([df['NAME'], df['SPECIALIZATION'], df['FREQUENCY']])

    judges = judges[:10]
    selected_judge = judges[0][0]
    petition.judge = selected_judge
    petition.save()

    context = {'judges':judges}
    html_template = loader.get_template('home/allocate_judges.html')
    return HttpResponse(html_template.render(context, request))



def get_status_flow(request):
    context = {}
    html_template = loader.get_template('home/case_status_flow.html')
    return HttpResponse(html_template.render(context, request))



## Module 2: AI Smart Legal AID

# AI Case Analysis Combined (4 models)

use_model = True
@require_POST
@login_required(login_url="/login/")
def get_query_analysis(request, id=None):
    case = UploadCaseFile.objects.get(id=id)
    input = case.uploadfile_description
    print(">>>>>>>>>>>>",case,input)
    pred_dict = judgement_pred_bigru(input)
    judgement_pred = int(pred_dict)
    # 2. Similar Cases Retrieval
    # similarcases, sim_cases, case_probs = [],[],[]
    similarcases, sim_cases, case_probs = similarcase(input)

    # 3. Law Suggestion
    # sim_prob_statues, sim_statues, statue_probs = [],[],[]
    sim_prob_statues, sim_statues, statue_probs = similarstat(input)

    # 4. Timeline Prediction
    print(input)
    timeline =  get_timeline_pred(input)
    print(timeline)


    context = {'prediction' : judgement_pred,
                'case':case,
                    'timeline' : timeline,
                    'similarcases': dumps(similarcases),
                    'sim_cases':dumps(sim_cases),
                    'case_probs': dumps(case_probs),
                    'sim_prob_statues' : dumps(sim_prob_statues),
                    'sim_statues': dumps(sim_statues),
                    'statue_probs': dumps(statue_probs)}
    
    
    html_template = loader.get_template('home/upload_cases2.html')
    return HttpResponse(html_template.render(context, request))


## Similar Cases

use_model = True
@require_POST
@login_required(login_url="/login/")
def get_similar_cases(request, id=None):

    query = UploadCaseFile.objects.get(id=id)
    
    all_similarcases, similar_cases, case_probs = similarcase(query.uploadfile_description)
    print(">>>>>>>",id, query, query.uploadfile_description)
    print(all_similarcases)

    similar_case_content = []
    case_content=[]
    
    for sim_case in similar_cases:
        sim_case = Case.objects.get(case_name=sim_case)
        similar_case_content.append((sim_case.id, sim_case.case_name, sim_case.case_description[0:100]))
        case_content.append((sim_case.id, sim_case.case_name, sim_case.case_description[0::]))

    context = {'case' : query, 'similar_cases': similar_case_content,'case_probs':case_probs,'case_content':case_content}

    html_template = loader.get_template('home/similar_cases.html')
    return HttpResponse(html_template.render(context, request))

 
## Relevant Statutes

use_model = True
@require_POST
@login_required(login_url="/login/")
def get_relevant_statues(request, id=None):

    case = UploadCaseFile.objects.get(id=id)
    _, sim_statues, statue_probs = similarstat(case.uploadfile_description)
    case.relevant_statues = dumps(sim_statues)
    case.save()

    similar_statue_content = []
    for statue in sim_statues:
        statues = Statutes.objects.get(sec_name=statue)
        similar_statue_content.append((statues.sec_name, statues.sec_title[0:50], statues.sec_def[0:70]))
    print(similar_statue_content)

    context = {'case' : case, 'similar_statue_content': similar_statue_content}

    html_template = loader.get_template('home/relevant_statues.html')
    return HttpResponse(html_template.render(context, request))



def view_case(request, id=None):
    case = Case.objects.get(case_name=id)
    print("Hello>>> ",case)
    context = {'case': case}

    html_template = loader.get_template('home/view_case.html')
    return HttpResponse(html_template.render(context, request))


## Case Document Translation

def translate(request):
    
    form = UploadFileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            file_content = request.FILES['uploadfile'].read()
            file_content = file_content.decode('UTF-8')  

            language = request.POST.get("dropdown", "")
            print("Language:", language)
            translated = get_translated(file_content, language)

            context = {'language': language,'before_trans': file_content, 'translated': translated, 'form': form}
        
        html_template = loader.get_template('home/translate.html')
        return HttpResponse(html_template.render(context, request))

    context = {'form':form}
    html_template = loader.get_template('home/translate.html')
    return HttpResponse(html_template.render(context, request))

## Judgement Prediction

def predict_judgement(request):    
    form = UploadFileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            file_content = request.FILES['uploadfile'].read()
            file_content = file_content.decode('UTF-8')
            prediction = judgement_pred_bigru(file_content)

            context = {'prediction': prediction , 'form': form}
        
        html_template = loader.get_template('home/translate.html')
        return HttpResponse(html_template.render(context, request))

    context = {'form':form}
    html_template = loader.get_template('home/translate.html')
    return HttpResponse(html_template.render(context, request))







## Supporting Views

def relevant_statue_retrieval(request):
    files = UploadCaseFile.objects.all()
    for f in files:
        f.uploadfile_description = f.uploadfile_description[0:70] + '...'
    files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/statute_retrieval.html')
    return HttpResponse(html_template.render(context, request))


def all_cases(request):
    files = Case.objects.all()
    for f in files:
        f.case_description = f.case_description[0:100] + '...'
    files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/all_cases.html')
    return HttpResponse(html_template.render(context, request))


@require_POST
@login_required(login_url="/login/")

def sec(request):
    
    input1=request.POST.get("SecNo", "")
    output=getDef(int(input()))

    sec_def=Sec(sec_name=input1,sec_def=output)
    sec_def.save()
    context={'output':output}

    html_template = loader.get_template('home/sec_def.html')
    return HttpResponse(html_template.render(context, request))
                                                

# data_path = "/home/local/ZOHOCORP/subha-12455/Desktop/sih2022/ai_works/AILA-Artificial-Intelligence-for-Legal-Assistance/AILA_2019_dataset/Object_casedocs/"
# statues_path = "/home/local/ZOHOCORP/subha-12455/Desktop/sih2022/ai_works/AILA-Artificial-Intelligence-for-Legal-Assistance/AILA_2019_dataset/Object_statutes/"

@require_POST
@login_required(login_url="/login/")

def h_verify(request):
    
    input=request.POST.get("hearNo", "")
    output=verify(input())
    print(output)
    context={'output':output}

    html_template = loader.get_template('home/hearing_home.html')
    return HttpResponse(html_template.render(context,h_verify, request))

@require_POST
@login_required(login_url="/login/")
def addCasetoDB(request):
    context = {}
    Case.objects.all().delete()
    for case_path in os.listdir(data_path):
        
        case_path_new = data_path + '/' + case_path        
        # read case
        case_filename = case_path
        content = ""
        if ".txt" in case_filename:
            with open(case_path_new, 'r') as f:
                for line in f.readlines():
                    content += line.strip()
                
            case_description = content
            case_status = "completed"

            new_case = Case(case_name=case_filename.split('.')[0], case_description=case_description, case_status=case_status)
            new_case.save()

        
    # for statue_path in os.listdir(statues_path):
        
    #     statue_path_new = statues_path + '/' + statue_path        
    #     # read case
    #     case_filename = statue_path
    #     print(case_filename)
    #     content = ""
    #     if ".txt" in case_filename:
    #         print(case_filename)
    #         with open(statue_path_new, 'r') as f:
    #             lines = f.readlines()
    #             title = lines[0].strip()[7:]
    #             for line in lines[1:]:
    #                 content += line.strip()[6:]

    #         sec_title = title
    #         case_description = content

    #         new_case = Statutes(sec_name=case_filename.split('.')[0],sec_title=sec_title, sec_def=case_description)
    #         new_case.save()


    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def analysis(request):
    context = {}

    html_template = loader.get_template('home/analysis.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    form=TodoForm()
    todo_list=Todo.objects.order_by('id')
    context = {'segment': 'index','todo_list' : todo_list ,'form' : form}


    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
