from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path('status/', views.LabStatusView.as_view(), name='lab_status'),
    path('toggle/', views.EnterExitToggleView.as_view(), name='in-out_toggle'),
    path('graph/', views.LogGraphView.as_view(), name='log_graph'),
    path('webcam/', views.capture, name='webcam'),
]
