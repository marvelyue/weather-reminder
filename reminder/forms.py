from django import forms
from models import Reminder

class AddReminderForm(forms.Form):
   zipcode = forms.CharField(
       required=True,
       label="Zipcode",
       error_messages={'required': 'Please input zipcode'},
       widget=forms.TextInput(
           attrs={
               'placeholder': "zipcode",
               'class': 'form-control',
           }
       )
   )
   reminder = forms.ChoiceField(
       choices=list(Reminder.WARNING_CHOICE),
       widget=forms.Select(
           attrs={
               'class': 'form-control',
           }
       )
   )
