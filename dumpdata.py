import django
from django.core.management import call_command
from dotenv import load_dotenv


# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
load_dotenv()

django.setup()

with open("db.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", stdout=f)
