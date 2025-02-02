# forms.py
from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('resume_file',)
        labels = {
            'resume_file': ' '
        }
        widgets = {
        'resume_file': forms.FileInput(attrs={'title': 'resume',"class":"form-control"})
        }
        
