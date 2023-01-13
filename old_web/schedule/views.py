from datetime import datetime, time, timedelta
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
import os
import subprocess
from schedule.models import Line, Schedule, ShellDuty
from .forms import ScheduleBuildForm

def get_icon_str_for_status(status: str) -> str:
    if (status == 'Completed'):
        return 'text-bg-success'
    elif (status == 'Pending'):
        return 'text-bg-info'

    return ''

def map_schedule_dto_vm(schedule: Schedule):
    schedule_vm = {}

    schedule_vm['name'] = schedule.name
    schedule_vm['start_date'] = schedule.start_date
    schedule_vm['end_date'] = schedule.end_date
    schedule_vm['submission_date_time'] = schedule.submission_date_time
    schedule_vm['status'] = schedule.status
    schedule_vm['icon'] = get_icon_str_for_status(schedule.status)

    return schedule_vm

@login_required
def index(request):

    schedules = [map_schedule_dto_vm(schedule_dto) for schedule_dto in Schedule.objects.all()]
    paginator = Paginator(schedules, per_page=2)

    page = request.GET.get('page')
    if page == None:
        page = paginator.num_pages

    page_obj = paginator.get_page(page)

    duties = ShellDuty.objects.select_related('duty')
    shell_duties = {}

    for shell_duty in duties:
        start_date = shell_duty.start_date_time.date()

        if start_date not in shell_duties:
            shell_duties[start_date] = []

        shell_duties[start_date].append(shell_duty)

    # TODO: need to account for auth_group
    lines = Line.objects.select_related('org')
    shell = {}

    for line in lines:
        start_date = line.start_date_time.date()

        if start_date not in shell:
            shell[start_date] = []

        shell[start_date].append(line)

    context = {'page_obj': page_obj, 'schedules': schedules, 'shell': shell, 'shell_duties': shell_duties }

    return render(request, 'schedule/index.html', context)

@login_required
def download(request):
    filename = request.GET['file']
    file_path = os.path.join(settings.MEDIA_ROOT, 'schedules', filename)
    print(file_path)

    if (os.path.exists(file_path)):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/csv')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    return Http404

@login_required
def build(request):
    print('--------------------------------')
    print(request.POST)

    if request.POST:
        print('Populate form')
        form = ScheduleBuildForm(request.POST)
        print(form.scheduleName)


    #subprocess.Popen(['python', 'autoscheduler/main.py'])

    return redirect('index')