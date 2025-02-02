from django.shortcuts import render ,get_object_or_404,redirect
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import requests
import pandas as pd
from pdfreader import SimplePDFViewer, PageDoesNotExist
from django.db.models import Q
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import en_core_web_lg

# Load SpaCy's pre-trained language model
nlp = spacy.load("en_core_web_lg")

def calculate_similarity(resume_content, job_description):
    # Process the texts with SpaCy
    doc_resume = nlp(resume_content)
    doc_job = nlp(job_description)
    
    # Get the vectors for both documents
    resume_vector = doc_resume.vector.reshape(1, -1)
    job_vector = doc_job.vector.reshape(1, -1)
    
    # Calculate cosine similarity between the resume and job description
    similarity_score = cosine_similarity(resume_vector, job_vector)
    
    return similarity_score[0][0]  # Get the similarity score (single value)

def extract_text_from_pdf(resume_file):
    
    import fitz  # Make sure PyMuPDF is imported
    
    text = ""
    # Open the resume_file properly
    resume_file.open('rb')  # Open the file in binary mode
    with fitz.open(stream=resume_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    resume_file.close()  # Close the file after reading
    return text


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!")
            login(request, user)  # Automatically log the user in after registration
            return redirect('jobs:upload_resume')  # Redirect to upload page or wherever you want
    else:
        form = UserCreationForm()
    
    return render(request, 'jobs/register.html', {'form': form})


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a resume already exists for the user
            try:
                resume = Resume.objects.get(user=request.user)  # Get the existing resume
                # Update the existing resume
                resume.resume_file = form.cleaned_data['resume_file']
            except Resume.DoesNotExist:
                # If resume doesn't exist, create a new one
                resume = form.save(commit=False)
                resume.user = request.user  # Assign the current user
            
            resume.save()  # Save the Resume instance (new or updated)

            # Extract text from PDF and save it
            resume_file = resume.resume_file
            resume_content = extract_text_from_pdf(resume_file)
            resume.resume_content = resume_content
            resume.save()  # Save the updated Resume instance with text content

            return redirect('jobs:results')
    else:
        form = ResumeForm()

    return render(request, "jobs/upload_resume.html", {'form': form})



@login_required
def results(request):
    # Get the logged-in user's resume content
    try:
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        resume = None

    # List to store tuples of (job, similarity_score)
    matching_jobs_with_scores = []

    if resume and resume.resume_content:
        # Get all job descriptions from the Job model
        jobs = Job.objects.all()

        for job in jobs:
            if job.description:  # Ensure job description is not empty or None
                # Calculate the similarity between resume content and job description
                similarity = calculate_similarity(resume.resume_content, job.description)
                
                # Only consider jobs with similarity score of 0.7 or higher
                if similarity >= 0.7:
                    matching_jobs_with_scores.append((job, similarity))

        # Sort the jobs by similarity score in descending order
        matching_jobs_with_scores.sort(key=lambda x: x[1], reverse=True)

    # Extract only the jobs from the sorted list
    matching_jobs = [job for job, score in matching_jobs_with_scores]

    return render(request, 'jobs/results.html', {
        'matching_jobs': matching_jobs
    })


def test(request):
    pass