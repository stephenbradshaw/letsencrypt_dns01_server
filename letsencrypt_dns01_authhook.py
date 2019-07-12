#!/usr/bin/env python
import os
import json
import time
import sys
import os

domain = os.environ['CERTBOT_DOMAIN']
validation = os.environ['CERTBOT_VALIDATION']

r = '_acme-challenge.' + domain.rstrip('.') + '.'
bp = ''
if sys.path[0]:
    bp = sys.path[0] + os.sep
config_name = bp +  'config.json'

config = json.load(open(config_name))

print 'Validation string %s for domain %s' %(validation, domain)

if r in config.keys():
    fn = bp + config[r][0].lstrip('file://')
    print "Writing to file %s" %(fn)
    open(fn, 'w').write(validation)

time.sleep(10)