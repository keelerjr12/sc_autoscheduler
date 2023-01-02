from django.db import models
from django.contrib.auth.models import Group

class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'org'

class Line(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    num = models.IntegerField()
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)

    start_date_time = models.DateTimeField()
    fly_go = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'shell_line'

class DutyType(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'duty_type'

class Duty(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    duty_type = models.ForeignKey(DutyType, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'duty'

class ShellDuty(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    duty = models.ForeignKey(Duty, on_delete=models.CASCADE)

    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'shell_duty'