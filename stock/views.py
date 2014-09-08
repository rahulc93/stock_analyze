from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader

from django.http import Http404

import csv
import json

import os
from os import listdir
from os.path import isfile, join

import datetime
from datetime import date


from stock.models import Stock

import matplotlib.pyplot as plt

def stock(request):
    stock_entry_list = Stock.objects.all()
    context = {'stock_entry_list': stock_entry_list}
    return render(request, 'stock/stock.html', context)

def stock_enter(request):
    mypath = join(os.getcwd(), 'stock/resources')
    print '\nLooking for .CSV files in %s' % mypath
    files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and f.endswith('.CSV') ]
    print '\nThe following %s .CSV files have been found in %s -' % (len(files), mypath)
    for count, f in enumerate(files):
        print 'File (%s/%s): %s' %(count + 1, len(files), f)
    stock_list = Stock.objects.all()
    field_names = ''
    for filename in files:
        day, month, year = filename.split('.CSV')[0][2:4], filename.split('.CSV')[0][4:6], filename.split('.CSV')[0][6:]
        if len(year) == 2:
            year = '20' + year
        print '\nEntering data from file (%s/%s) %s' % (files.index(filename) + 1, len(files), filename)
        with open(join(mypath, filename)) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for count, row in enumerate(spamreader):
                row_entry_list = ', '.join(row).split(', ')
                if count == 0 and not field_names:
                    field_names = row_entry_list
                elif count > 0:
                    q = Stock(SC_CODE = row_entry_list[0], SC_NAME = row_entry_list[1], SC_GROUP = row_entry_list[2], SC_TYPE = row_entry_list[3], OPEN = float(row_entry_list[4]), HIGH = float(row_entry_list[5]), LOW = float(row_entry_list[6]), CLOSE = float(row_entry_list[7]), LAST = float(row_entry_list[8]), PREVCLOSE = float(row_entry_list[9]), NO_TRADES = float(row_entry_list[10]), NO_OF_SHRS = float(row_entry_list[11]), NET_TURNOV = float(row_entry_list[12]), DATE = datetime.date(int(year), int(month), int(day)))
                    q.save()
                    print "Saving entry from file %s/%s with id %s, SC_NAME %s" % (files.index(filename) + 1, len(files), q.id, q.SC_NAME)
    return HttpResponse('All the entries have been successfully added. Call the "stock" method to view the current database.')

def stock_clearall(request):
    stock_list = Stock.objects.all()
    if not stock_list:
        return HttpResponse('Database is empty. Nothing to delete.')
    else:
        total = Stock.objects.count()
        for count, stock in enumerate(stock_list):
            print 'Deleting stock %s / %s entry with id %s, SC_NAME %s' % (count + 1, total, stock.id, stock.SC_NAME)
            stock.delete()
        return HttpResponse('All the entries have been successfully deleted. Call the "stock" method to view the current database.')

def goc(request, comp_code, date):
    if len(date) < 8:
        return HttpResponse('Invalid Date Format. Try DDMMYYYY')
    date = datetime.date(int(date[4:]), int(date[2:4]), int(date[:2]))
    result = Stock.objects.filter(SC_CODE = comp_code, DATE = date)
    if not result:
        return HttpResponse('No results found')
    else:
        response_data = {}
        response_data['SC_CODE'] = result[0][0].SC_CODE
        response_data['SC_NAME'] = result[0][0].SC_NAME
        response_data['DATE'] =  str(date.day) + '-' + str(date.month) + '-' + str(date.year)
        response_data['OPEN'] = result[0][0].OPEN
        response_data['CLOSE'] = result[0][0].CLOSE
        return HttpResponse(json.dumps(response_data, indent = 4), content_type = 'application/json')

def goc_range(request, comp_code, start_date, end_date):
    start_date = datetime.date(int(start_date[4:]), int(start_date[2:4]), int(start_date[:2]))
    end_date = datetime.date(int(end_date[4:]), int(end_date[2:4]), int(end_date[:2]))
    stock = []
    while start_date <= end_date:
        curr_stock =  Stock.objects.filter(SC_CODE = comp_code, DATE = start_date)
        if not curr_stock:
            print 'No entries found for Date:  %s' % start_date
        else:
            stock.append(curr_stock)
        start_date += datetime.timedelta(days = 1)
    print '%s stock entries have been found' % len(stock)
    OPEN = []
    CLOSE = []
    response_data = {}
    response_data['SC_CODE'] = stock[0][0].SC_CODE
    response_data['SC_NAME'] = stock[0][0].SC_NAME
    for currstock in stock:
        OPEN.append(currstock[0].OPEN)
        CLOSE.append(currstock[0].CLOSE)
        response_data[str(currstock[0].DATE.day) + '-' + str(currstock[0].DATE.month) + '-' + str(currstock[0].DATE.year)] = {
            'Open': currstock[0].OPEN,
            'Close': currstock[0].CLOSE
        }
    print OPEN
    print CLOSE
    plt.figure(1)
    plt.subplot(211)
    plt.plot(OPEN)
    plt.ylabel('Open')
    plt.title('Opening Values')
    plt.annotate('Maximum (%s)' % max(OPEN), xy=(OPEN.index(max(OPEN)), max(OPEN)), xytext=(len(OPEN) / 2, max(OPEN) + 2),
            arrowprops=dict(facecolor='black', shrink=0.05),
            )
    plt.annotate('Minimum (%s)' % min(OPEN), xy=(OPEN.index(min(OPEN)), min(OPEN)), xytext=(len(OPEN) / 2, min(OPEN) + 2),
            arrowprops=dict(facecolor='red', shrink=0.05),
            )
    plt.grid(True)
    plt.subplot(212)
    plt.plot(CLOSE)
    plt.ylabel('Close')
    plt.title('Closing Values')
    plt.annotate('Maximum (%s)' % max(CLOSE), xy=(CLOSE.index(max(CLOSE)), max(CLOSE)), xytext=(len(CLOSE) / 2, max(CLOSE) + 2),
            arrowprops=dict(facecolor='black', shrink=0.05),
            )
    plt.annotate('Minimum (%s)' % min(CLOSE), xy=(CLOSE.index(min(CLOSE)), min(CLOSE)), xytext=(len(CLOSE) / 2, min(CLOSE) + 2),
            arrowprops=dict(facecolor='red', shrink=0.05),
            )
    plt.grid(True)
    plt.show()
    return HttpResponse(json.dumps(response_data, indent = 4), content_type = 'application/json')