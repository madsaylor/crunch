#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from crunch import main_crunch
import os
import json
import sys

if len(sys.argv) > 1:    
    key = sys.argv[1]
    url_query = 'https://api.crunchbase.com/v/3/people?query=founder&user_key={}'.format(key)

    if not os.path.exists('people.json'):
        r = requests.get(url_query)
        resp = r.json()
        with open('people.json', 'w') as f:
            f.write(r.text.encode('utf-8'))
        print 'File of {} bytes written'.format(os.path.getsize('people.json'))
    else:
        with open('people.json', 'r') as f:
            resp = json.loads(f.read().decode('utf-8'))

    nb_pages = resp["data"]["paging"]['number_of_pages']

    print 'nb_pages : ' + str(nb_pages)

    start = 0
    main_crunch(start, nb_pages, 'company' + str(start) + '.csv', key)
else:
    print 'Please provide API key, like this: "python main.py 93423ddshjksf8w4f"'