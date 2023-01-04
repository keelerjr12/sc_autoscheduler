from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import csv
from .models import Pilot

def map_to_viewmodel(p: Pilot):
    quals = {}
    org = ''
    
    for qual in p.quals.all():
        quals[qual.name] = 'X'

    if len(p.org.all()) != 0:
        org = p.org.all()[0].name

    pilot = {
        'id': p.id,
        'name': f'%s, %s' % (p.last_name, p.first_name),
        'assigned_org': org,
        'quals': {
            'ops_supervisor': 'X' if 'Operations Supervisor' in quals.keys() else '',
            'sof': 'X' if 'SOF' in quals.keys() else '',
            'rsu_controller': 'X' if 'RSU Controller' in quals.keys() else '',
            'rsu_observer': 'X' if 'RSU Observer' in quals.keys() else '',
            'pit_ip': 'X' if 'PIT IP' in quals.keys() else ''
        }
    } 

    return pilot

@login_required
def index(request):
    header = ['Name', 'Assigned Flight', 'Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer', 'PIT IP']

    pilot_rs = Pilot.objects.filter(auth_group__name__in=request.user.groups.values_list('name', flat=True)).prefetch_related('quals', 'org')
    pilots = [map_to_viewmodel(p) for p in pilot_rs]
    flight_orgs = ['', 'M', 'N', 'O', 'P', 'X']
    quals = ['', 'X']

    context = {'header': header, 'pilots': pilots, 'flight_orgs': flight_orgs, 'quals': quals}

    return render(request, 'personnel/index.html', context)