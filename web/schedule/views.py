from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
import os
import subprocess
from schedule.models import Line, ShellDuty

@login_required
def index(request):

    schedule_path = os.path.join(settings.MEDIA_ROOT, 'schedules')
    schedules = os.listdir(schedule_path)    

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

    context = {'schedules': schedules, 'shell': shell, 'shell_duties': shell_duties}

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
    subprocess.Popen(['python', 'autoscheduler/main.py'])

    return redirect('index')