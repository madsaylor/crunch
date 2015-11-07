#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import time

import csv

key = ''
url_query = 'https://api.crunchbase.com/v/3/people?query=founder&user_key={}'.format(key)


url_people_start = 'https://api.crunchbase.com/v/3/'
url_people_end = '?user_key={}'.format(key)

#Test url 
url_test_people = 'https://api.crunchbase.com/v/3/persons/david-goldweitz?user_key={}'.format(key)


list_properties = ['permalink','api_path','web_path','name','also_known_as','short_description','description', 'primary_role', 'role_company',
'role_investor','role_group','role_school','founded_on','founded_on_trust_code','is_closed','closed_on',
'closed_on_trust_code','num_employees_min','num_employees_max','stock_exchange','stock_symbol','total_funding_usd',
'number_of_investments','homepage_url','created_at','updated_at']

sep  ='|'
timer = 0.1
debug = True

def parDict(item):

	res= {}
	
	for key, value in item.iteritems():
	
		#print type(value)
		if type(value) == unicode :
			
			res[key]= value.encode('ascii', 'replace') 
			
		else:
			res[key]= value

	return res


def reqWithRetry(url):

	success = False
	max_rety = 5
	data = {}
	while not success and max_rety > 0:
		try:
			r = requests.get(url)
			if r.status_code == 200:
				data = r.json()
				success = True
			else:
				print 'req error : ' + url
				print r.status_code, r.text
				max_rety = max_rety - 1
		except:
			print 'Error retry lef : ', str(max_rety)
			max_rety = max_rety - 1

	#time.sleep( timer )
	return data



def testDegree(degree_items):

	try:
		for degree_item in degree_items:

			school = degree_item['relationships']['school']['properties']['permalink']
			if school == 'columbia-business-school':
				return True

		return False

	except Exception, e:
		print 'error object'
		return False
	
def getCompanyforPeople(url_people):

	line = ''

	resp_people =  reqWithRetry(url_people)
	if len(resp_people) == 0 :
		return line

	degree_items = resp_people['data']['relationships']['degrees']['items']

	if testDegree(degree_items):
		
		properties = resp_people['data']['relationships']['primary_affiliation']['item']['relationships']['organization']['properties']	

		for propertie in list_properties:
			
			val =  properties[propertie]
			if val is not None:
				#print val
				if type(val) == bool:
					if val:
						line = line + 'true'+sep
					else:
						line = line + 'false'+sep
				elif type(val) == int:
					line = line +str(properties[propertie])+sep
				else:
					line = line + properties[propertie]+sep
			else:
				#print 'null'
				line = line +sep
		
		line = line + json.dumps(properties)

	return line

def getCompanyforPeople2(url_people):

	resp_people =  reqWithRetry(url_people)
	if len(resp_people) == 0 :
		return {}	

	degree_items = resp_people['data']['relationships']['degrees']['items']

	if testDegree(degree_items):
		
		properties = resp_people['data']['relationships']['founded_companies']['items']
		return properties

	else:
		return {}	


def testPage(i, writercsv):

	resp =  reqWithRetry(url_query+'&page='+str(i+1))

	items = resp["data"]["items"]

	for item in items:

		permalink = item['properties']['api_path']

		url_people = url_people_start+permalink+url_people_end

		prop = getCompanyforPeople2(url_people)

		if len(prop) != 0:
			print 'Company match : ' + item['properties']['organization_permalink']

			if debug :
				print url_people

			print prop
			for item in prop:
				writercsv.writerow(parDict(item['properties']))

				#writercsv.writerow(item['properties'])



		#line = getCompanyforPeople(url_people)

	#	if len(line) != 0:
	#		print 'Company match : ' + item['properties']['organization_permalink']
	#		file.write(line+'\n')


def main_crunch(start_idx, end_idx, filename):
	
	with open(filename, 'w') as file:
			
		fieldnames = list_properties
		writer = csv.DictWriter(file, fieldnames=list_properties)

		writer.writeheader()

		for i in range(start_idx, end_idx+1):

			print 'page : ' + str(i+1)
			testPage(i, writer)
				



