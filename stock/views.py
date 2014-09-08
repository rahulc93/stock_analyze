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
    """

    Function to display the current database in a tabular form. If empty database then display appropriate message.

    :return: The stock.html template is getting rendered and a dictionary is passed to it for printing all the stock entries

    """
    stock_entry_list = Stock.objects.all()  # list of all Stock entries
    context = {'stock_entry_list': stock_entry_list}  # dictionary to be used in the template
    return render(request, 'stock/stock.html', context)  # call the template passing the dictionary to it

def stock_enter(request):
    """

    Function to read the CSV files and enter the data to the database. The csv module is used for this purpose.
    The 'resources' folder is scanned for the CSV files. All the files found from there are listed in the terminal, and they are read and stored one by one.

    :return: HttpResponse containing a message saying either all entries have been added, or no CSV files found in the resources folder to add

    """
    mypath = join(os.getcwd(), 'stock/resources')  # path to the 'resources' folder
    print '\nLooking for .CSV files in %s' % mypath
    files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and f.endswith('.CSV') ]  # list of CSV files found, if any
    if not files:  # no CSV files present in the resources folder
        return HttpResponse('No ".CSV" files are placed in the resources folder. Could not add data.')  # display error message
    else:  # CSV files found
        print '\nThe following %s .CSV files have been found in %s -' % (len(files), mypath)
        for count, f in enumerate(files):
            print 'File (%s/%s): %s' %(count + 1, len(files), f)
        stock_list = Stock.objects.all()
        for filename in files:  # iterating through the list of CSV filenames found
            # calculating the date by reading the filename (present in ddmmyy format by default)
            day, month, year = filename.split('.CSV')[0][2:4], filename.split('.CSV')[0][4:6], filename.split('.CSV')[0][6:]
            if len(year) == 2:
                year = '20' + year  # if year is of 2 digits, add '20' to its beginning
            print '\nEntering data from file (%s/%s) %s' % (files.index(filename) + 1, len(files), filename)
            with open(join(mypath, filename)) as csvfile:  # open the file
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')  # read the contents
                for count, row in enumerate(spamreader):
                    row_entry_list = ', '.join(row).split(', ')  # list of all the elements in the current row separated by comma
                    if count > 0:  # the current row is not the field-name row
                        # save the entry to database
                        q = Stock(SC_CODE = row_entry_list[0], SC_NAME = row_entry_list[1], SC_GROUP = row_entry_list[2], SC_TYPE = row_entry_list[3], OPEN = float(row_entry_list[4]), HIGH = float(row_entry_list[5]), LOW = float(row_entry_list[6]), CLOSE = float(row_entry_list[7]), LAST = float(row_entry_list[8]), PREVCLOSE = float(row_entry_list[9]), NO_TRADES = float(row_entry_list[10]), NO_OF_SHRS = float(row_entry_list[11]), NET_TURNOV = float(row_entry_list[12]), DATE = datetime.date(int(year), int(month), int(day)))
                        q.save()
                        print "Saving entry from file %s/%s with id %s, SC_NAME %s" % (files.index(filename) + 1, len(files), q.id, q.SC_NAME)
        return HttpResponse('All the entries have been successfully added. Call the "stock" method to view the current database.')

def stock_clearall(request):
    """

    Function to clear the whole database entry-by-entry.

    :return: HttpResponse containing a message saying either deletion is successful or no entries found in database for deleting

    """
    stock_list = Stock.objects.all()  # list of all entries currently present in database
    if not stock_list:  # empty database, nothing to delete
        return HttpResponse('Database is empty. Nothing to delete.')
    else:  # entries found in database for deleting
        total = Stock.objects.count()  # total number of entries present
        for count, stock in enumerate(stock_list):
            print 'Deleting stock %s / %s entry with id %s, SC_NAME %s' % (count + 1, total, stock.id, stock.SC_NAME)
            stock.delete()  # delete entry
        return HttpResponse('All the entries have been successfully deleted. Call the "stock" method to view the current database.')

def goc(request, comp_code, date):
    """

    Function to determine the Opening and Closing values for the company with specified Company Code and for specified date.
    The appropriate entry is extracted from the database, and a dictionary is created containing the Company Code, Company Name, the Date specified, and the Opening and Closing values. This dictionary is then printed in the webpage in a JSON format.

    :arg comp_code: the unique Company Code

    :arg date: the date (DDMMYYYY format) for which the Opening and Closing values are to be found

    :return: HttpResponse containing the required dictionary in JSON format

    """
    if len(date) < 8:  # invalid date format provided
        return HttpResponse('Invalid Date Format. Try DDMMYYYY')
    date = datetime.date(int(date[4:]), int(date[2:4]), int(date[:2]))  # create a datetime.date object for the given date string
    result = Stock.objects.filter(SC_CODE = comp_code, DATE = date)  # extract the required entry
    if not result:  # required entry not present in database
        return HttpResponse('No results found')  # display error message
    else:  # required entry found in database
        # create the dictionary to print it in JSON format
        response_data = {}
        response_data['SC_CODE'] = result[0].SC_CODE  # unique company code
        response_data['SC_NAME'] = result[0].SC_NAME  # company name
        response_data['DATE'] =  str(date.day) + '-' + str(date.month) + '-' + str(date.year)  # date (DD-MM-YYYY format)
        response_data['OPEN'] = result[0].OPEN  # Opening value
        response_data['CLOSE'] = result[0].CLOSE  # Closing value
        return HttpResponse(json.dumps(response_data, indent = 4), content_type = 'application/json')

def goc_range(request, comp_code, start_date, end_date):
    """

    Function to calculate a list of all Opening and Closing values for the company with the specified unique comp_code and date ranging between the specified start_date and end_date
    The list of appropriate entries is extracted from the database, and a dictionary is prepared which stored the required data. The dictionary is printed in JSON format.
    Also, using matplotlib.pyplot we plot 2 graphs, one for Opening values and the other for Closing values.
    The graphs will be displayed in a separate window. Once that window is closed, the webpage is rendered and the JSON data is displayed there.

    :arg comp_code: unique company code

    :arg start_date: starting date for the duration

    :arg end_date: ending date for the duration

    :return: HttpResponse containing the dictionary which contains all the data for the given range of dates and is displayed in JSON format. Also the graph is displayed before the webpage gets rendered.

    """
    
    # create start_date and end_date datetime.date objects based on values provided by user
    start_date = datetime.date(int(start_date[4:]), int(start_date[2:4]), int(start_date[:2]))
    end_date = datetime.date(int(end_date[4:]), int(end_date[2:4]), int(end_date[:2]))
    stock = []  # list of required stock entries lying between the specified range of dates
    while start_date <= end_date:  # keep iterating from start_date to end_date
        curr_stock =  Stock.objects.filter(SC_CODE = comp_code, DATE = start_date)  # extract stock entry having date value of start_date
        if not curr_stock:  # no entry with such a date present
            print 'No entries found for Date:  %s' % start_date  # display error message
        else:  # desired database entry present
            stock.append(curr_stock)  # append the stock entry to the list
        start_date += datetime.timedelta(days = 1)  # change start_date to the next day
    print '%s stock entries have been found' % len(stock)
    OPEN = []  # list of all Opening values from the required stock entries
    CLOSE = []  # list of all Closing values from the required stock entries
    response_data = {}  # dictionary storing the JSON data
    response_data['SC_CODE'] = stock[0][0].SC_CODE  # company unique code
    response_data['SC_NAME'] = stock[0][0].SC_NAME  # company name
    for currstock in stock:  # iterate through the list of stock entries
        OPEN.append(currstock[0].OPEN)  # append Opening value for current stock to list
        CLOSE.append(currstock[0].CLOSE)  # append Closing value for current stock to list
        # add to the dictionary the Opening and Closing values for current date
        response_data[str(currstock[0].DATE.day) + '-' + str(currstock[0].DATE.month) + '-' + str(currstock[0].DATE.year)] = {
            'Open': currstock[0].OPEN,
            'Close': currstock[0].CLOSE
        }
    # create the graphs
    plt.figure(1)
    plt.subplot(211)  # plot a graph for OPEN
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
    plt.subplot(212)  # plot a graph for CLOSE
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
    plt.show()  # display the graph
    return HttpResponse(json.dumps(response_data, indent = 4), content_type = 'application/json')