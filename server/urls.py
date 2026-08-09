from django.urls import path
from app.views import view_scraped_data, start_scrap_data, update_vacancy_status

urlpatterns = [
    path("", view_scraped_data, name="scraped_data_view"),
    path("scrap/", start_scrap_data, name="scrap_data_view"),
    path("vacancy/<int:vacancy_id>/status/", update_vacancy_status, name="update_vacancy_status"),
]
