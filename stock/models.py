from django.db import models
import datetime
from django.utils import timezone
import csv
import datetime
from datetime import datetime, date, time, timedelta

# Create your models here.

class Stock(models.Model):
    SC_CODE = models.CharField(max_length = 200)
    SC_NAME = models.CharField(max_length = 200)
    SC_GROUP = models.CharField(max_length = 200)
    SC_TYPE = models.CharField(max_length = 200)
    OPEN = models.FloatField(default = 0)
    HIGH = models.FloatField(default = 0)
    LOW = models.FloatField(default = 0)
    CLOSE = models.FloatField(default = 0)
    LAST = models.FloatField(default = 0)
    PREVCLOSE = models.FloatField(default = 0)
    NO_TRADES = models.FloatField(default = 0)
    NO_OF_SHRS = models.FloatField(default = 0)
    NET_TURNOV = models.FloatField(default = 0)
    DATE = models.DateField(max_length = 200)

    #filename = 'EQ040614.CSV'
    #with open(filename) as csvfile:
     #   spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|') # a single row which keeps iterating
      #  for count, row in enumerate(spamreader):
       #     row_entry_list = ''.join(row).split(',')
        #    if count == 0:
         #       field_names = row_entry_list
          #      for field in field_names:
           #         field = models.CharField(max_length = 200)
