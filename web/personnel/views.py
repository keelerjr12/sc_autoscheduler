from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, render
import csv
from .models import Organization, Pilot, LOX

@login_required
def index(request):
    header = ['Assigned Flight', 'Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer', 'PIT IP']

    lox = LOX.objects.all()

    context = {'header': header, 'lox': lox}
    #file = 'res/lox.csv'

    #with open(file, newline='') as csvfile:
    #    reader = csv.reader(csvfile, delimiter=',')
    #    header = next(reader, None)

    #    roster = [row for row in reader]
    #    context = {'header': header, 'roster': roster}

    return render(request, 'personnel/index.html', context)