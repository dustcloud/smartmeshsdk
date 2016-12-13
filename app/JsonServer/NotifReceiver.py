import pprint
import json
from bottle import route, run, request

LOGFILE = 'NotifReceiver.log'
pp = pprint.PrettyPrinter(indent=4)

@route('<path:path>', method='ANY')
def all(path):
    output  = []
    output += ['='*80]
    output += ['method: {0}'.format(request.method)]
    output += ['path:   {0}'.format(path)]
    output += ['body:   {0}'.format(pp.pformat(json.loads(request.body.getvalue())))]
    output += ['']
    output  = '\n'.join(output)
    print output
    with open(LOGFILE,'a') as f:
        f.write(output)

run(host='localhost', port=1880)