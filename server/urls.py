from django.urls import path
from app.views import view_scraped_data

urlpatterns = [
    path("", view_scraped_data, name="scraped_data_view"),
]
