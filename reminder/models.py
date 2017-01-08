
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Reminder(models.Model):
   ALWAYS = 0
   RAIN = 1
   SNOW = 2
   TEMPDROP3F = 3
   TEMPRISE3F = 4
   MAX_CHOICES = 5
   WARNING_TEXT = [
       'Always',
       'Raining tomorrow',
       'Snowing tomorrow',
       'Temperature dropping by 3F tomorrow',
       'Temperature rising by 3F tomorrow',
   ]
   WARNING_CHOICE = [(i, WARNING_TEXT[i]) for i in range(MAX_CHOICES)]
   user = models.ForeignKey(User)
   zipcode = models.CharField(max_length=30)
   warning_event = models.IntegerField(default=0, choices=WARNING_CHOICE)
   reminder_sent = models.DateField(default=datetime.min, blank=True)

   def __str__(self):
       return self.user.get_username() + '_' + self.zipcode
