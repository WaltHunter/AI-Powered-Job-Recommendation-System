from django.core.management.base import BaseCommand
from jobs.utils import scrape_and_save_jobs

class Command(BaseCommand):
    help = 'Scrapes jobs from Indeed and saves them to the database'

    def handle(self, *args, **kwargs):
        scrape_and_save_jobs()
        self.stdout.write(self.style.SUCCESS('Successfully scraped and saved jobs!'))
