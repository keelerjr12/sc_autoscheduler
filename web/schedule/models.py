from django.db import models

class Pilot(models.Model):
    id = models.IntegerField(primary_key=True)
    prsn_id = models.IntegerField()
    last_name = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)

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