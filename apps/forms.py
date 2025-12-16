from django import forms
from apps.models.enrollment import *
from apps.models.leads import *

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['full_name', 'phone', 'source']


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student_name', 'course', 'operator', 'price_paid']
