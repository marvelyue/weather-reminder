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

def get_weather(zipcode):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\"%s\")" % zipcode
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    result = urllib2.urlopen(yql_url).read()
    data = dict()
    try:
        data = json.loads(result)['query']['results']['channel']
    except:
        print(traceback.format_exc())
    return data

def generate_weather_string(data):
   return "It will be %s in %s on %s. The temperature will be %s to %s %s." % (
       data['item']['forecast'][1]['text'],
       data['location']['city'],
       data['item']['forecast'][1]['date'],
       data['item']['forecast'][1]['low'],
       data['item']['forecast'][1]['high'],
       data['units']['temperature'],
   )

def test_email(request):
   user_id = None
   if request.user.is_authenticated():
       user_id = request.user.id
   else:
       return HttpResponseRedirect("/admin/login/")
   reminders = Reminder.objects.filter(user_id=user_id)
   # De-duplicate zipcode.
   zipcodes = set()
   for reminder in reminders:
       zipcodes.add(reminder.zipcode)
   body = "Dear %s,\n\n" % request.user.username
   for zipcode in zipcodes:
       body += generate_weather_string(get_weather(zipcode)) + "\n"
   body += "\nBest,\nWeather Reminder"
   print body
   message = EmailMessage("Email Testing", body, to=[request.user.email])
   message.send()
   return HttpResponseRedirect("/")


def secret_trigger(request):
   percentage = float(request.GET.get('percentage', "100"))
   num_reminders = percentage * len(Reminder.objects.all()) / 100
   reminders = Reminder.objects.filter(reminder_sent__lt=date.today())
   zip_reminders_map = defaultdict(list)
   # Aggregate by zipcode
   for reminder in reminders:
       zip_reminders_map[reminder.zipcode].append(reminder)
   count = 0
   # Aggregate by user email
   emails = defaultdict(dict)
   for zipcode in zip_reminders_map:
       if percentage < 100 and count > num_reminders:
           break
       warnings = generate_warnings(get_weather(zipcode))
       reminder_list = zip_reminders_map[zipcode]
       for reminder in reminder_list:
           if reminder.warning_event in warnings.keys():
               emails[(reminder.user.username, reminder.user.email)][zipcode] = warnings[reminder.warning_event]
               reminder.reminder_sent = datetime.now()
               reminder.save()
       count += len(reminder_list)
   sent_list = []
   for user_id, email in emails:
       body = "Dear %s,\n\n" % user_id
       for zipcode in emails[(user_id, email)]:
           body += emails[(user_id, email)][zipcode] + "\n"
       body += "\n Best,\nWeather Reminder"
       message = EmailMessage("Weather reminder", body, to=[email])
       message.send()
       sent_list.append(email)
   return HttpResponse("Sent Emails to: " + ", ".join(sent_list))

def generate_warnings(data):
  warnings = dict()
  try:
      today_weather = data['item']['forecast'][0]
      tomorrow_weather = data['item']['forecast'][1]
      OKAY_CODES = ('19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                    '31', '32', '33', '34', '36', '44')
      RAIN_CODES = ('0', '1', '3', '4', '6', '8', '9', '10', '11', '12', '37', '38', '39',
                    '40', '45', '47')
      SNOW_CODES = ('5', '7', '13', '14', '15', '16', '17', '18', '35', '41', '42', '43', '46')
      warning_text = generate_weather_string(data)
      warnings[Reminder.ALWAYS] = warning_text
      if tomorrow_weather['code'] in RAIN_CODES:
          warnings[Reminder.RAIN] = warning_text + " It will be raining tomorrow, please remember to take your umbrella."
      if tomorrow_weather['code'] in SNOW_CODES:
          warnings[Reminder.SNOW] = warning_text + " It will be snowing tomorrow, please drive carefully."
      if (float(tomorrow_weather['low']) - float(today_weather['low']) <= -3 or
                      float(tomorrow_weather['high']) - float(today_weather['high']) <= -3):
          warnings[Reminder.TEMPDROP3F] = warning_text + " The temperature will drop by more than 3 F, please wear warmer clothes."
      if (float(tomorrow_weather['low']) - float(today_weather['low']) >= 3 or
                      float(tomorrow_weather['high']) - float(today_weather['high']) >= 3):
          warnings[Reminder.TEMPRISE3F] = warning_text + " The temperature will rise by more than 3 F."
  except:
      print(traceback.format_exc())
  return warnings
