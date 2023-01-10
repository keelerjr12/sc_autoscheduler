from django.db import models
from django.contrib.auth.models import Group

class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    tims_id = models.IntegerField()
    last_name = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'person'

class PersonLine(models.Model):
    id = models.IntegerField(primary_key=True)
    auth_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    ausm_tier = models.IntegerField()

    org = models.ManyToManyField('Organization', through='PilotOrganization')

    quals = models.ManyToManyField(
        'Qualification',
        through= 'PilotQualification'
    )

    class Meta:
        managed = False
        db_table = 'person_line'

class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'org'

class PilotOrganization(models.Model):
    person = models.ForeignKey(PersonLine, db_column='person_id', on_delete=models.CASCADE, primary_key=True)
    org = models.ForeignKey(Organization, db_column='org_id', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pilot_org'
        unique_together = (
            "person_id",
            "org_id",
        )

class QualificationType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'qual_type'

class Qualification(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.ForeignKey(QualificationType, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'qual'

class PilotQualification(models.Model):
    person = models.ForeignKey(PersonLine, db_column='person_id', on_delete=models.CASCADE, primary_key=True)
    qual = models.ForeignKey(Qualification, db_column='qual_id', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'pilot_qual'
        unique_together = (
            "person_id",
            "qual_id"
        )
