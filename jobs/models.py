from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    site = models.CharField(max_length=255)
    job_url = models.URLField(unique=True)
    job_url_direct = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=100, null=True, blank=True)
    date_posted = models.DateTimeField()
    salary_source = models.CharField(max_length=255, null=True, blank=True)
    interval = models.CharField(max_length=50, null=True, blank=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    job_level = models.CharField(max_length=255, null=True, blank=True)
    job_function = models.CharField(max_length=255, null=True, blank=True)
    company_industry = models.CharField(max_length=255, null=True, blank=True)
    listing_type = models.CharField(max_length=255, null=True, blank=True)
    emails = models.EmailField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    company_url = models.URLField(null=True, blank=True)
    company_url_direct = models.URLField(null=True, blank=True)
    company_addresses = models.TextField(null=True, blank=True)
    company_num_employees = models.CharField(max_length=255, null=True, blank=True)
    company_revenue = models.CharField(max_length=255, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
    






class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    resume_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}'s Resume"