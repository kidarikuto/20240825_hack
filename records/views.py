from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EntryExitLog
from django.db.models import Max


class LabStatusView(LoginRequiredMixin, View):
    def get(self, request):
        latest_logs = EntryExitLog.objects.all().order_by('-timestamp')[:10]
        in_lab_users = [
            log.user.username for log in latest_logs if log.action == 'IN'
        ]
        in_lab_count = len(in_lab_users)

        return render(request, 'records/status.html', {
            'latest_logs': latest_logs,
            'in_lab_users': in_lab_users,
            'in_lab_count': in_lab_count
        })

class EnterLabView(LoginRequiredMixin, View):
    def post(self, request):
        EntryExitLog.objects.create(user=request.user, action='IN')
        return redirect('records:lab_status')

class ExitLabView(LoginRequiredMixin, View):
    def post(self, request):
        EntryExitLog.objects.create(user=request.user, action='OUT')
        return redirect('records:lab_status')
