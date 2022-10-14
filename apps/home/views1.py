# -*- encoding: utf-8 -*-

from multiprocessing import context
# from xxlimited import new
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import Todo,Case,Sec,UploadCaseFile,Statutes
from django.views.decorators.http import require_POST
from .forms import TodoForm,UploadFileForm
import os
from json import dumps
from natsort import natsorted

from .get_sec_def import getDef
from .getTranslate import getTranslate
from .jpbigru import *
from .similar_cases import *
from .relevant_statues import *
# from .timeline_prediction import *
from .indictrans import *
from django.core.files.storage import FileSystemStorage
from django.conf import settings



IMAGE_FILE_TYPES = ['txt']

pred_dict = {0 : 'Rejected'}
pred_dict = {0 : 'Accepted'}

def case_analysis(request):

    form = UploadFileForm(request.POST or None, request.FILES or None)
    if form.is_valid():

        file_content = request.FILES['uploadfile'].read()
        print(file_content)
        file_content = file_content.decode('UTF-8')
        obj = form.save(commit=False)
        print("Object ID:",obj.id)

        with open(settings.MEDIA_ROOT + '/new_cases/' + obj.uploadfile.url.split('/')[-1], 'r') as f:
            for line in f.readlines():
                obj.uploadfile_description += line.strip()

        obj.save()

        # # 1. Judgement Prediction
        # pred_dict = judgement_pred_bigru(file_content)
        
        # obj.prediction = pred_dict
        # obj.save()


        # judgement_pred = int(pred_dict)

        # # 2. Similar Cases Retrieval
        # # similarcases, sim_cases, case_probs = [],[],[]
        # similarcases, sim_cases, case_probs = similarcase(file_content)

        # # 3. Law Suggestion
        # # sim_prob_statues, sim_statues, statue_probs = [],[],[]
        # sim_prob_statues, sim_statues, statue_probs = similarstat(file_content)

        # # 4. Timeline Prediction
        # timeline = get_timeline_pred(file_content)

        # 5. Translation



        files = UploadCaseFile.objects.all()
        for f in files:
            f.uploadfile_description = f.uploadfile_description[0:100] + '...'
        files = files[::-1]

        context = {'form' : form,
                    'files':files,
        }
                    # 'prediction' : judgement_pred,
                    # 'timeline' : timeline,
                    # 'similarcases': dumps(similarcases),
                    # 'sim_cases':dumps(sim_cases),
                    # 'case_probs': dumps(case_probs),
                    # 'sim_prob_statues' : dumps(sim_prob_statues),
                    # 'sim_statues': dumps(sim_statues),
                    # 'statue_probs': dumps(statue_probs)}

        html_template = loader.get_template('home/case_analysis.html')
        return HttpResponse(html_template.render(context, request))


    files = UploadCaseFile.objects.all()
    for f in files:
            f.uploadfile_description = f.uploadfile_description[0:80] + '...'
    # files = files[::-1]
    context = {'form' : form, 'files': files}
    html_template = loader.get_template('home/case_analysis.html')
    return HttpResponse(html_template.render(context, request))


use_model = True
@require_POST
@login_required(login_url="/login/")
def get_query_analysis(request, id=None):
    case = UploadCaseFile.objects.get(id=id)
    input = case.uploadfile_description
    
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
    # timeline =  get_timeline_pred(input)
    # print(timeline)


    context = {'prediction' : judgement_pred,
                'case':case,
                    # 'timeline' : timeline,
                    'similarcases': dumps(similarcases),
                    'sim_cases':dumps(sim_cases),
                    'case_probs': dumps(case_probs),
                    'sim_prob_statues' : dumps(sim_prob_statues),
                    'sim_statues': dumps(sim_statues),
                    'statue_probs': dumps(statue_probs)}
    
    
    html_template = loader.get_template('home/upload_cases2.html')
    return HttpResponse(html_template.render(context, request))



def all_cases(request):
    files = Case.objects.all()
    for f in files:
        f.case_description = f.case_description[0:100] + '...'
    files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/all_cases.html')
    return HttpResponse(html_template.render(context, request))
   

# def uploaded_cases(request):
#     files = UploadCaseFile.objects.all()
#     for f in files:
#         f.uploadfile_description = f.uploadfile_description[0:70] + '...'
#     files = files[::-1]
#     context = { 'files': files[0:10]}
#     html_template = loader.get_template('home/uploaded_cases.html')
#     return HttpResponse(html_template.render(context, request))

def similar_case_retrieval(request):
    files = UploadCaseFile.objects.all()
    for f in files:
        f.uploadfile_description = f.uploadfile_description[0:70] + '...'
    files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/case_retrieval.html')
    return HttpResponse(html_template.render(context, request))

def relevant_statue_retrieval(request):
    files = UploadCaseFile.objects.all()
    for f in files:
        f.uploadfile_description = f.uploadfile_description[0:70] + '...'
    files = files[::-1]
    context = { 'files': files[0:10]}
    html_template = loader.get_template('home/statute_retrieval.html')
    return HttpResponse(html_template.render(context, request))


use_model = True
@require_POST
@login_required(login_url="/login/")
def get_similar_cases(request, id=None):

    query = UploadCaseFile.objects.get(id=id)
    _, similar_cases, case_probs = similarcase(query.uploadfile_description)
    print(similar_cases)

    similar_case_content = []
    for sim_case in similar_cases:
        sim_case = Case.objects.get(case_name=sim_case)
        similar_case_content.append((sim_case.case_name, sim_case.case_description[0:100]))

    context = {'case' : query, 'similar_cases': similar_case_content,'case_probs':case_probs}

    html_template = loader.get_template('home/similar_cases.html')
    return HttpResponse(html_template.render(context, request))

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



    # #with open(newfile.uploadfile.path,'r') as f:
    # #    for line in f.readlines():
    # #        case_content += line.strip()
    # form=UploadFileForm()

    # case_content = ''

    # language=request.POST.get("dropdown", "")
    # print(language)
    # output=getTranslate(language,case_content)

    # context={'output':output,'language':language,'form':form}

    # html_template = loader.get_template('home/translator.html')
    # return HttpResponse(html_template.render(context, request))




@require_POST
@login_required(login_url="/login/")

def sec(request):
    
    input=request.POST.get("SecNo", "")
    output=getDef(int(input))

    sec_def=Sec(sec_name=input,sec_def=output)
    sec_def.save()
    context={'output':output}

    html_template = loader.get_template('home/sec_def.html')
    return HttpResponse(html_template.render(context, request))
                                                

data_path = "/home/local/ZOHOCORP/subha-12455/Desktop/sih2022/ai_works/AILA-Artificial-Intelligence-for-Legal-Assistance/AILA_2019_dataset/Object_casedocs/"
statues_path = "/home/local/ZOHOCORP/subha-12455/Desktop/sih2022/ai_works/AILA-Artificial-Intelligence-for-Legal-Assistance/AILA_2019_dataset/Object_statutes/"

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

        elif load_template == 'high_court':
            return HttpResponseRedirect(reverse('high_court:high_court'))

        elif load_template == 'page4':
            return HttpResponseRedirect(reverse('page4:page4'))

        elif load_template == 'sec_def':
            return HttpResponseRedirect(reverse('sec_def:sec_def'))

        elif load_template == 'map':
            return HttpResponseRedirect(reverse('map:map'))

        elif load_template == 'page5':
            return HttpResponseRedirect(reverse('page5:page5'))

        elif load_template == 'pending':
            return HttpResponseRedirect(reverse('pending:pending'))

        elif load_template == 'contact':
            return HttpResponseRedirect(reverse('contact:contact'))

        elif load_template == 'Period_of_limitation':
            return HttpResponseRedirect(reverse('Period_of_limitation:Period_of_limitation'))


        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
