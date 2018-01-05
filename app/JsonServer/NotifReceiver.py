import pprint
import json
from bottle import route, run, request

LOGFILE = 'NotifReceiver.log'
pp = pprint.PrettyPrinter(indent=4)

@route('<path:path>', method='ANY')
def all(path):
    output  = []
    output += ['='*80]
    output += ['method:      {0}'.format(request.method)]
    output += ['path:        {0}'.format(path)]
    output += ['headers:     {0}'.format('\n       - '.join(['{0}={1}'.format(h, request.headers.get(h)) for h in request.headers.keys()] ))]
    output += ['body:        {0}'.format(json.loads(request.body.getvalue()))]
    output += ['body_pp:     {0}'.format(pp.pformat(json.loads(request.body.getvalue())))]
    output += ['']
    output  = '\n'.join(output)
    print output
    with open(LOGFILE,'a') as f:
        f.write(output)

run(host='localhost', port=1880)