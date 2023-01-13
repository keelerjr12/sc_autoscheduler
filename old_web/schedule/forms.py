from django import forms

class ScheduleBuildForm(forms.Form):
    scheduleName = forms.CharField(label='Name', max_length=100)