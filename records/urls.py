from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path('status/', views.LabStatusView.as_view(), name='lab_status'),
    path('enter/', views.EnterLabView.as_view(), name='enter_lab'),
    path('exit/', views.ExitLabView.as_view(), name='exit_lab'),
    path('graph/', views.LogGraphView.as_view(), name='log_graph'),
]
