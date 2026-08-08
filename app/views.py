import threading

from django.shortcuts import render
from app.tasks import scrap_data


def view_scraped_data(request):
    ...


def start_scrap_data(request):
    ...
