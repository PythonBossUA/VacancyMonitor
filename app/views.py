import threading


from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.db.models import Q
from app.models import Vacancy
from app.tasks import scrap_data


def view_scraped_data(request):
    queryset = Vacancy.objects.select_related("company").order_by("-publication_date")

    search_query = request.GET.get("search", "").strip()
    selected_category = request.GET.get("category", "").strip()
    selected_status = request.GET.get("status", "").strip()
    selected_is_active = request.GET.get("is_active", "").strip()

    categories = (
        Vacancy.objects.values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | Q(company__name__icontains=search_query)
        )

    if selected_category:
        queryset = queryset.filter(category=selected_category)

    if selected_status == "none":
        queryset = queryset.filter(status__isnull=True)
    elif selected_status:
        queryset = queryset.filter(status=selected_status)

    if selected_is_active == "1":
        queryset = queryset.filter(is_active=True)
    elif selected_is_active == "0":
        queryset = queryset.filter(is_active=False)

    paginator = Paginator(queryset, 50)
    page = request.GET.get("page")

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
        "categories": categories,
        "selected_category": selected_category,
        "selected_status": selected_status,
        "selected_is_active": selected_is_active,
        "status_choices": Vacancy.STATUS_CHOICES,
    }

    return render(request, "view_scraped_data.html", context=context)


@require_POST
def update_vacancy_status(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    new_status = request.POST.get("status", "").strip()
    valid_statuses = [choice[0] for choice in Vacancy.STATUS_CHOICES]
    if new_status in valid_statuses:
        vacancy.status = new_status
    else:
        vacancy.status = None

    vacancy.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
def delete_all_unactive_vacancies(request):
    Vacancy.objects.filter(is_active=False).delete()
    return redirect(request.META.get("HTTP_REFERER", "/"))


def start_scrap_data(request):
    scrap = threading.Thread(
        target=scrap_data,
        daemon=True,
    )
    scrap.start()

    return render(request, "scraping_process_started.html")
