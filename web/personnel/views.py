from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, render
import csv
from .models import Pilot

@login_required
def index(request):
    user = request.user.groups.all()
    print(user)
    pilots_rs = Pilot.objects.all()
    header_quals = ['Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer']

    pilots = []
    for pilot_rs in pilots_rs:
        pilot = {'last_name': pilot_rs.last_name, 'first_name': pilot_rs.first_name}
        quals = []
        for qual in header_quals:
            q = ' '
            for pq in pilot_rs.quals.all():
                if pq.name == qual:
                    q = 'X'
            quals.append(q)
        pilot['quals'] = quals
        pilots.append(pilot)

    context = {'header': header_quals, 'pilots': pilots}
    #file = 'res/lox.csv'

    #with open(file, newline='') as csvfile:
    #    reader = csv.reader(csvfile, delimiter=',')
    #    header = next(reader, None)

    #    roster = [row for row in reader]
    #    context = {'header': header, 'roster': roster}

    return render(request, 'personnel/index.html', context)