from django import forms
from django.db.models import get_model
import urllib

class IssueFilter(forms.Form):
    FIELDS = {'project': 'name', 'status': 'name', 'priority': 'name',
              'category': 'name', 'author': 'username', 'assigned': 'username'}


    project = forms.ModelChoiceField(queryset=get_model('zero', 'Project').objects.all(), required=False, empty_label="Any")
    status = forms.ModelChoiceField(queryset=get_model('zero', 'Status').objects.all(), required=False, empty_label="Any")
    priority = forms.ModelChoiceField(queryset=get_model('zero', 'Priority').objects.all(), required=False, empty_label="Any")
    category = forms.ModelChoiceField(queryset=get_model('zero', 'Category').objects.all(), required=False, empty_label="Any")
    author = forms.ModelChoiceField(queryset=get_model('auth', 'User').objects.all(), required=False, empty_label="Any")
    #assigned = forms.ModelChoiceField(queryset=get_model('auth', 'User').objects.all(), required=False, empty_label="Any")

    def get_encoded_cleaned_data(self):
        z = dict( (k, getattr(v, IssueFilter.FIELDS[k]) if v else 'none') for k, v in self.cleaned_data.iteritems())
        return urllib.urlencode(z)
