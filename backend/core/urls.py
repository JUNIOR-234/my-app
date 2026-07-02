from django.contrib import admin
from django.urls import path
from chat.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls), # Exposes all endpoints + interactive Swagger docs at /api/docs automatically!
]
