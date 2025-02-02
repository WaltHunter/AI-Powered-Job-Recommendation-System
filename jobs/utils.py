import pandas as pd
import datetime
from django.utils import timezone
import deepl
from .models import Job
from jobspy import scrape_jobs


from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import requests

def google_translate_text(text, target_lang="en"):
    """Translate text using Google Translate API with API key."""
    api_key = "Your API Key"  # Your API Key
    url = f"https://translation.googleapis.com/language/translate/v2"
    
    params = {
        'q': text,
        'target': target_lang,
        'format': 'text',
        'key': api_key  # Pass the API key here
    }

    if text and text.strip():
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()  # Check for HTTP errors
            result = response.json()
            return result['data']['translations'][0]['translatedText']
        except requests.exceptions.RequestException as e:
            print(f"Error translating text: {e}")
            return text
    return text

def translate_text(text, target_lang="en"):
    """Wrapper function to call Google Translate."""
    if text and text.strip():
        return google_translate_text(text, target_lang)
    return text  # Return original text if it's empty or None




def scrape_and_save_jobs():
    # Scrape jobs
    jobs = scrape_jobs(
        site_name=["indeed"],
        results_wanted=50000,
        hours_old=720,
        country_indeed='Belgium',
    )

    # Ensure jobs is a DataFrame if it's not already
    if not isinstance(jobs, pd.DataFrame):
        jobs = pd.DataFrame(jobs)

    for index, row in jobs.iterrows():
        # Convert date_posted to a timezone-aware datetime
        date_posted = row['date_posted']
        if pd.notna(date_posted):
            if isinstance(date_posted, pd.Timestamp):
                if date_posted.tzinfo is None:
                    date_posted = timezone.make_aware(date_posted, timezone.get_current_timezone())
            elif isinstance(date_posted, datetime.datetime):
                if date_posted.tzinfo is None:
                    date_posted = timezone.make_aware(date_posted, timezone.get_current_timezone())
            elif isinstance(date_posted, datetime.date):
                date_posted = timezone.make_aware(pd.to_datetime(date_posted), timezone.get_current_timezone())
            else:
                date_posted = None  # Handle as needed
        else:
            date_posted = None  # Or handle as needed

        # Handle NaN values for decimal fields
        def handle_nan(value):
            try:
                return float(value) if pd.notna(value) else None
            except ValueError:
                return None

        min_amount = handle_nan(row.get('min_amount'))
        max_amount = handle_nan(row.get('max_amount'))

        # Translate job title and description if necessary
        job_title = row.get('title')
        job_description = row.get('description')

        translated_title = translate_text(job_title)
        translated_description = translate_text(job_description)

        # Update or create job entries in the database
        job, created = Job.objects.update_or_create(
            job_url=row['job_url'],  # Unique identifier
            defaults={
                'site': row.get('site'),
                'job_url_direct': row.get('job_url_direct'),
                'title': translated_title,  # Use translated title
                'company': row.get('company'),
                'location': row.get('location'),
                'job_type': row.get('job_type'),
                'date_posted': date_posted,
                'salary_source': row.get('salary_source'),
                'interval': row.get('interval'),
                'min_amount': min_amount,
                'max_amount': max_amount,
                'currency': row.get('currency'),
                'is_remote': row.get('is_remote'),
                'job_level': row.get('job_level'),
                'job_function': row.get('job_function'),
                'company_industry': row.get('company_industry'),
                'listing_type': row.get('listing_type'),
                'emails': row.get('emails'),
                'description': translated_description,  # Use translated description
                'company_url': row.get('company_url'),
                'company_url_direct': row.get('company_url_direct'),
                'company_addresses': row.get('company_addresses'),
                'company_num_employees': row.get('company_num_employees'),
                'company_revenue': row.get('company_revenue'),
                'company_description': row.get('company_description'),
            }
        )

        if created:
            print(f"Created new job: {job.title}")
        else:
            print(f"Updated existing job: {job.title}")
