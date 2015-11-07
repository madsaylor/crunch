#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
from pprint import pformat

import csv

requests.packages.urllib3.disable_warnings() 
url_query = 'https://api.crunchbase.com/v/3/people?query=founder&user_key={}'

wrong_people_file = 'wrong_people.txt'
url_people_start = 'https://api.crunchbase.com/v/3/'
url_people_end = '?user_key={}'

possible_series = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
list_properties = ['permalink','api_path','web_path','name','also_known_as','short_description','description', 'primary_role', 'role_company',
'role_investor','role_group','role_school','founded_on','founded_on_trust_code','is_closed','closed_on',
'closed_on_trust_code','num_employees_min','num_employees_max','stock_exchange','stock_symbol','total_funding_usd',
'number_of_investments','homepage_url','created_at','updated_at', 'founders', 'seed_rounds']

list_properties += ['venture_round_{}'.format(series) for series in possible_series]

sep = '|'
timer = 0.1
debug = True


def parDict(item):
    res = {}
    for key, value in item.iteritems():
        #print type(value)
        if type(value) == unicode:
            res[key] = value.encode('ascii', 'replace')
        else:
            res[key] = value

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
    resp_people =  reqWithRetry(url_people)
    if len(resp_people) == 0:
        return {}

    degree_items = resp_people['data']['relationships']['degrees']['items']

    if testDegree(degree_items):
        properties = resp_people['data']['relationships']['founded_companies']['items']
        return properties

    else:
        with open(wrong_people_file, 'a') as f:
            # print resp_people['data']['properties']['permalink']
            f.write(u'{}\n'.format(resp_people['data']['properties']['permalink'].encode('ascii', 'replace')))
        return {}


def processPage(i, writercsv, key):
    people_response = reqWithRetry(url_query.format(key) + '&page=' + str(i+1))
    people_list = people_response["data"]["items"]
    j = 0
    for person in people_list:
        wrong_people = None
        with open(wrong_people_file, 'r') as f:
            wrong_people = [s.strip() for s in f.readlines()];

        if person['properties']['permalink'] not in wrong_people:
            permalink = person['properties']['api_path']
            url_people = url_people_start + permalink + url_people_end.format(key)
            company_list = getCompanyforPeople(url_people)

            j += 1
            person_name = u'{} of {}: {} {}'.format(
                j,
                len(people_list),
                person['properties']['first_name'], 
                person['properties']['last_name']
            )
            if len(company_list) != 0:
                print 'Founder match : {}'.format(person_name)
                if debug:
                    print url_people

                # print prop
                for company in company_list:
                    writeCompany(company, writercsv, key)

            else:
                print u'Founder {} not matched the condition'.format(person_name)
        else:
            print u'* Founder {} already checked *'.format(person['properties']['permalink'])

def writeCompany(company, writercsv, key):
    org_permalink = company['properties']['permalink']
    
    url_founders = 'https://api.crunchbase.com/v/3/organizations/{}/founders?user_key={}'
    url_rounds = 'https://api.crunchbase.com/v/3/organizations/{}/funding_rounds?user_key={}'
    founders_api_response = reqWithRetry(url_founders.format(org_permalink, key))
    rounds_api_response = reqWithRetry(url_rounds.format(org_permalink, key))
    
    founders, rounds = [], []
    if 'data' not in founders_api_response:
        pass
    elif 'items' in founders_api_response['data']:
        founders = founders_api_response['data']['items']
    elif 'item' in founders_api_response['data']:
        founders.append(founders_api_response['data']['item'])

    if 'data' not in rounds_api_response:
        pass
    elif 'items' in rounds_api_response['data']:
        rounds = rounds_api_response['data']['items']
    elif 'item' in rounds_api_response['data']:
        rounds.append(rounds_api_response['data']['item'])

    if len(founders) > 0:
        company['properties']['founders'] = ', '.join([
            '{} {}'.format(f['properties']['first_name'], f['properties']['last_name']) for f in founders
        ])

    if len(rounds) > 0:
        seed_rounds = [i for i in rounds if i['properties']['funding_type'] == 'seed']
        venture_rounds = [i for i in rounds if i['properties']['funding_type'] == 'venture']
    else:
        seed_rounds, venture_rounds = [], []


    seed_rounds_strings = []
    for r in seed_rounds:        
        money = r['properties']['money_raised_usd']
        if money is None:
            money = 'Not Specified'
        else:
            money = '${:,}'.format(int(money)).replace(',','\'')

        seed_rounds_strings.append(
            u'{} ({})'.format(
                money,
                r['properties']['announced_on'].split('-')[0]
            )
        )

    company['properties']['seed_rounds'] = ', '.join(seed_rounds_strings)

    for venture_round in venture_rounds:
        series = venture_round['properties']['series']        
        if series in possible_series:
            column_name = 'venture_round_{}'.format(series)
            money = venture_round['properties']['money_raised_usd']
            if money is None:
                money = 'Not Specified'
            else:
                money = '${:,}'.format(int(money)).replace(',','\'')

            company['properties'][column_name] = '{} ({})'.format(
                money,
                venture_round['properties']['announced_on'].split('-')[0]
            )

    dict_to_write = dict((key,value) for key, value in company['properties'].iteritems() if key in list_properties)
    writercsv.writerow(parDict(dict_to_write))
    print 'Company {} written ro thet CSV file'.format(company['properties']['name'])

def main_crunch(start_idx, end_idx, filename, key):    
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=list_properties)
        writer.writeheader()

    for i in range(start_idx, end_idx):   
        with open(filename, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=list_properties)
            print 'page : {} of {}'.format(str(i+1), end_idx)
            processPage(i, writer, key)