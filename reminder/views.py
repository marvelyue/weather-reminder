import urllib2, urllib, json, traceback
from collections import defaultdict
from datetime import date, datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.mail import EmailMessage
from models import Reminder
from forms import AddReminderForm

def manage(request):
   user_id = None
   if request.user.is_authenticated():
       user_id = request.user.id
   else:
       return HttpResponseRedirect("/admin/login/")
   if request.method == 'POST':
       post_form = AddReminderForm(request.POST)
       if post_form.is_valid():
           zipcode = post_form.cleaned_data['zipcode']
           reminder = post_form.cleaned_data['reminder']
           Reminder.objects.create(user_id=user_id, zipcode=zipcode, warning_event=reminder)

   reminders = Reminder.objects.filter(user_id=user_id)
   form = AddReminderForm()
   return render(request, 'manage.html', {'form': form, 'reminders': reminders, 'logged_in': True})

def del_reminder(request):
   if not request.user.is_authenticated():
       return HttpResponseRedirect("/admin/login/")
   try:
       reminder_id = int(request.GET.get('id', ''))
       p = Reminder.objects.get(id=int(reminder_id))
       p.delete()
   except:
       pass
   return HttpResponseRedirect("/")
