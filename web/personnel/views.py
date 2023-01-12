import json
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import connection
from .models import Organization, PersonLine, PilotOrganization, PilotQualification, Qualification

def map_to_viewmodel(p: PersonLine):
    quals = {}
    org = ''
    
    for qual in p.quals.all():
        quals[qual.name] = 'X'

    if len(p.org.all()) != 0:
        org = p.org.all()[0].name

    pilot = {
        'id': p.id,
        'name': f'%s, %s' % (p.person.last_name, p.person.first_name),
        'assigned_org': org,
        'quals': {
            'ops_supervisor': 'X' if 'Operations Supervisor' in quals.keys() else '',
            'sof': 'X' if 'SOF' in quals.keys() else '',
            'rsu_controller': 'X' if 'RSU Controller' in quals.keys() else '',
            'rsu_observer': 'X' if 'RSU Observer' in quals.keys() else '',
            'ipc_pilot': 'X' if 'IPC Pilot' in quals.keys() else '',
            'fpc_pilot': 'X' if 'FPC Pilot' in quals.keys() else '',
            'fcf_pilot': 'X' if 'FCF Pilot' in quals.keys() else '',
            'pit_ip': 'X' if 'PIT IP' in quals.keys() else '',
            'sefe': 'X' if 'SEFE' in quals.keys() else ''
        }
    } 

    return pilot

@login_required
def index(request):
    pilot_rs = PersonLine.objects.filter(auth_group__name__in=request.user.groups.values_list('name', flat=True)).order_by('person__last_name', 'person__first_name').prefetch_related('person', 'quals', 'org')
    pilots = [map_to_viewmodel(p) for p in pilot_rs]
    flight_orgs = ['', 'M', 'N', 'O', 'P', 'X']
    quals = ['', 'X']

    context = {'pilots': pilots, 'flight_orgs': flight_orgs, 'quals': quals}

    return render(request, 'personnel/index.html', context)

@login_required
def person(request: HttpRequest, id: int):

    if request.method == 'POST':
        data = json.loads(request.body)

        person_id = data['person_id']
        assigned_org = data['org']

        if (assigned_org == ""):
            PilotOrganization.objects.filter(person_id=person_id).delete()
        else:
            person = PersonLine.objects.get(id=person_id)
            org = Organization.objects.get(name=assigned_org)

            defaults = {
                'person_id': person.id,
                'org_id': org.id
            }

            PilotOrganization.objects.update_or_create(defaults=defaults, person=person)
        
        quals_to_add = []
        quals_to_remove = []

        for qual, val in data['quals'].items():
            if val == '':
                quals_to_remove.append(qual)
            else:
                quals_to_add.append(qual)

        pilot_quals = [PilotQualification(person_id=person_id, qual_id=qual.id) for qual in Qualification.objects.filter(name__in=quals_to_add)]
        PilotQualification.objects.bulk_create(pilot_quals, ignore_conflicts=True)

        # this is needed due to Django being unable to handle composite primary keys
        # and only deleting by the primary key
        if len(quals_to_remove) > 0:
            with connection.cursor() as cursor:
                stmt = "DELETE FROM pilot_qual USING qual WHERE qual.id = pilot_qual.qual_id AND pilot_qual.person_id = %s AND qual.name IN (%s)" % ('%s', ','.join('%s' for i in quals_to_remove))
                params = quals_to_remove
                params.insert(0, person_id)
                cursor.execute(stmt, params)

    return HttpResponse("Success")
