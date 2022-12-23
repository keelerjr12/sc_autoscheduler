from django.db import models
from django.contrib.auth.models import Group

class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'orgs'

class Line(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    num = models.IntegerField()
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)

    start_date_time = models.DateTimeField()
    fly_go = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'shell_lines'