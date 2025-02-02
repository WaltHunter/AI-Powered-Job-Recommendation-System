from django.urls import path
from .views import *

app_name ="jobs"

urlpatterns = [
    path('upload_resume/', upload_resume, name='upload_resume'),
    path('/', upload_resume, name='upload_resume'),
    path('test/', test, name='test'),
    path("results/",results,name="results"),
]
