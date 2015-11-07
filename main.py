#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import requests
import json

from crunch import main_crunch

key = ''
url_query = 'https://api.crunchbase.com/v/3/people?query=founder&user_key={}'.format(key)

nb_page_per_thread = 200

list_thread = []

r = requests.get(url_query)
resp =  r.json()


nb_pages =  resp["data"]["paging"]['number_of_pages']

#nb_thread = nb_pages/nb_page_per_thread+1

print 'nb_pages : ' + str(nb_pages)
#print 'nb_thread : ' + str(nb_thread)

#for i in range(nb_thread):

#	startpos = nb_page_per_thread*i
#	endpos = nb_page_per_thread*(i+1)
#	filename = '_result'+str(i)+'.csv'

#	list_thread.append( threading.Thread(None, main_crunch, None, (startpos, endpos, filename) ) )
#	print 'Start Thread :' + str(i) +' ' + str(startpos) +' ' + str(endpos) +' ' + filename
#	list_thread[i].start() 


start = 547 
main_crunch(start, nb_pages, 'company'+str(start)+'.csv')
