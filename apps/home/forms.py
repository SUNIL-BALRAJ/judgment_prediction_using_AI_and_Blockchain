from fileinput import FileInput
from django import forms 
from .models import UploadCaseFile, UploadHearingFile, UploadHearingFile1


#DataFlair #File_Uploa

    

class TodoForm(forms.Form):
    text = forms.CharField(max_length=40, 
        widget=forms.TextInput(
            attrs={'class' : 'form-control', 'placeholder' : 'Upload Case files', 'aria-label' : 'Todo', 'aria-describedby' : 'add-btn'}))

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadCaseFile
        fields = [
        'uploadfile_name',
        'uploadfile_short_desc',
        'uploadfile',
        'category'
       
        ]
        widgets = {
            'uploadfile_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;height: 50px;',
                'placeholder': 'Name'
                }), 
            'uploadfile_short_desc': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;height: 50px;',
                'placeholder': 'Description'
                }),
            # 'uploadfile' : forms.ClearableFileInput(attrs={
            #     'class': "form-control",
            #     'style': 'max-width: 300px;height: 50px;',
            #     'placeholder': 'File'
            #     })

        }

# class UploadFileForm(forms.Form):
#     file = forms.FileField()

class UploadHearingFileForm1(forms.ModelForm):
    class Meta:
        model = UploadHearingFile1
        fields = [
            'h_uploadfile_name',
        'h_uploadfile', 
        ]
        widgets = {
            'uploadfile_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;height: 50px;',
                'placeholder': 'Hearing Name'
                }), 
            
            # 'uploadfile' : forms.ClearableFileInput(attrs={
            #     'class': "form-control",
            #     'style': 'max-width: 300px;height: 50px;',
            #     'placeholder': 'File'
            #     })

        }
