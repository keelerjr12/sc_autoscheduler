from django.db import models
from django.contrib.auth.models import Group

class LOX(models.Model):
    id = models.IntegerField(primary_key=True, db_column='id')
    auth_group_name = models.CharField(max_length=150)

    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)

    assigned_org = models.CharField(max_length=64)

    ops_supervisor = models.BooleanField(db_column='operations_supervisor')
    sof = models.BooleanField()
    rsu_controller = models.BooleanField()
    rsu_observer = models.BooleanField()

    pit_ip = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'vw_pilots_quals'

class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'orgs'

class Pilot(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    prsn_id = models.IntegerField()
    last_name = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    ausm_tier = models.IntegerField()

    org = models.ManyToManyField('Organization', through='PilotOrganization')
    #org = models.OneToOneField('PilotOrganization', on_delete=models.CASCADE)
    #org = models.ForeignKey('Organization', on_delete=models.CASCADE)

    quals = models.ManyToManyField(
        'Qualification',
        through= 'PilotQualification'
    )

    class Meta:
        managed = False
        db_table = 'pilots'

class Qualification(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'quals'

class PilotQualification(models.Model):
    pilot_id = models.ForeignKey(Pilot, db_column='pilot_id', on_delete=models.CASCADE)
    qual_id = models.ForeignKey(Qualification, db_column='qual_id', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pilots_quals'


class PilotOrganization(models.Model):
    pilot_id = models.ForeignKey(Pilot, db_column='pilot_id', on_delete=models.CASCADE)
    org_id = models.ForeignKey(Organization, db_column='org_id', on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'pilots_orgs'