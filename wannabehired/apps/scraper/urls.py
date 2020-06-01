from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.jobs),
    path('django-rq/', include('django_rq.urls'))
    # path('articles/<int:year>/', views.year_archive),
    # path('articles/<int:year>/<int:month>/', views.month_archive),
    # path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),
]