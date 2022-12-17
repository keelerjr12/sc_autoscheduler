from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, render
import csv
from .models import Organization, Pilot

@login_required
def index(request):
    pilots_rs = Pilot.objects.filter(auth_group__in=request.user.groups.all()).prefetch_related('quals')
    #print(pilots_rs.query)
    header_quals = ['Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer']
    header = ['Assigned Flight'] + header_quals

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
    
        org = pilot_rs.org.first()
        if (org == None):
            pilot['org'] = ""
        else:
            pilot['org'] = org.name

        pilot['quals'] = quals
        pilots.append(pilot)

    context = {'header': header, 'pilots': pilots}
    #file = 'res/lox.csv'

    #with open(file, newline='') as csvfile:
    #    reader = csv.reader(csvfile, delimiter=',')
    #    header = next(reader, None)

    #    roster = [row for row in reader]
    #    context = {'header': header, 'roster': roster}

    return render(request, 'personnel/index.html', context)