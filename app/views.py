import threading

from django.shortcuts import render
from app.tasks import scrap_data


def view_scraped_data(request):
    return render(request, "view_scraped_data.html")


def start_scrap_data(request):
    scrap = threading.Thread(
        target=scrap_data,
        daemon=True,
    )
    scrap.start()

    return render(request, "scraping_process_started.html")
