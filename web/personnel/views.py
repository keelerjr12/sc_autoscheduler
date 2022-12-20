from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import csv
from .models import LOX

@login_required
def index(request):
    header = ['Assigned Flight', 'Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer', 'PIT IP']

    lox = LOX.objects.filter(auth_group_name__in=request.user.groups.values_list('name', flat=True)).all()

    context = {'header': header, 'lox': lox}
    #file = 'res/lox.csv'

    #with open(file, newline='') as csvfile:
    #    reader = csv.reader(csvfile, delimiter=',')
    #    header = next(reader, None)

    return render(request, 'personnel/index.html', context)