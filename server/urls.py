from django.urls import path
from app.views import view_scraped_data, start_scrap_data

urlpatterns = [
    path("", view_scraped_data, name="scraped_data_view"),
    path("scrap/", start_scrap_data, name="scrap_data_view"),
]
