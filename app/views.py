import threading

from django.shortcuts import render
from app.tasks import scrap_data
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Vacancy


def view_scraped_data(request):
    queryset = Vacancy.objects.select_related('company').order_by('id')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    paginator = Paginator(queryset, 50)
    page = request.GET.get('page')

    try:
        vacancies = paginator.page(page)
    except PageNotAnInteger:
        vacancies = paginator.page(1)
    except EmptyPage:
        vacancies = paginator.page(paginator.num_pages)

    context = {
        "vacancies": vacancies,
        "total_count": paginator.count,
        "search_query": search_query,
    }

    return render(request, "view_scraped_data.html", context=context)


def start_scrap_data(request):
    scrap = threading.Thread(
        target=scrap_data,
        daemon=True,
    )
    scrap.start()

    return render(request, "scraping_process_started.html")
