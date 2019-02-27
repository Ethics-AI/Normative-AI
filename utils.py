from __future__ import print_function
import sys
import requests
from collections import namedtuple
from bs4 import BeautifulSoup

Meta = namedtuple('Meta', [
    'main_field',
    'journal',
    'title',
    'authors',
    'date',
    'codes',
    'pdf_link',
    'website_link',
    'text',
    'related_entries',
    'login_required'
])


def get(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)