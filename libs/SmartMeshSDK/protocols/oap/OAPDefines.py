COMMAND = {
    'GET'                    : 0x01,
    'PUT'                    : 0x02,
    'POST'                   : 0x03,
    'DELETE'                 : 0x04,
    'NOTIFICATION'           : 0x05,
}

RC = {
    'OK'                     : 0,
    'NOT_FOUND'              : 1,
    'NO_RESOURCES'           : 2,
    'UNK_PARAM'              : 3,
    'INV_VALUE'              : 4,
    'INV_ADDR'               : 5,
    'NO_SUPPORT'             : 6,
    'RD_ONLY'                : 7,
    'WR_ONLY'                : 8,
    'FEWER_BYTES'            : 9,
    'TOO_MANY_BYTES'         : 10,
    'UNK_ERROR'              : 11,
    'EXEC_SIZE'              : 12,
}

ADDRESS = {
    'info'                   : (0,),
    'main'                   : (1,),
    'digital_in'             : (2,),
    'digital_in/D0'          : (2,0),
    'digital_in/D1'          : (2,1),
    'digital_in/D2'          : (2,2),
    'digital_in/D3'          : (2,3),
    'digital_out'            : (3,),
    'digital_out/D4'         : (3,0),
    'digital_out/D5'         : (3,1),
    'digital_out/INDICATOR_0': (3,2),
    'analog'                 : (4,),
    'analog/A0'              : (4,0),
    'analog/A1'              : (4,1),
    'analog/A2'              : (4,2),
    'analog/A3'              : (4,3),
    'temperature'            : (5,),
    'pkgen/echo'             : (254,0),
    'pkgen'                  : (254,),
}

FIELDS = {
    'info' : [
        ('swRevMaj',         'INT8U',       'r'),
        ('swRevMin',         'INT8U',       'r'),
        ('swRevPatch',       'INT8U',       'r'),
        ('swRevBuild',       'INT16U',      'r'),
        ('appId',            'INT16U',      'r'),
        ('resetCounter',     'INT32U',      'r'),
        ('changeCounter',    'INT32U',      'r'),
    ],
    'main' : [
        ('destAddr',         'INT8U[16]',   'r/w'),
        ('destPort',         'INT16U',      'r/w'),
    ],
    'digital_in' : [
        ('enable',           'INT8U',       'r/w'),
        ('rate',             'INT32U',      'r/w'),
        ('sampleCount',      'INT16U',      'r/w'),
        ('dataFormat',       'INT8U',       'r/w'),
        ('value',            'INT8U',       'r'),
    ],
    'digital_out' : [
        ('value',            'INT8U',       'w'),
    ],
    'analog' : [
        ('enable',           'INT8U',       'r/w'),
        ('rate',             'INT32U',      'r/w'),
        ('sampleCount',      'INT8U',       'r/w'),
        ('dataFormat',       'INT8U',       'r/w'),
        ('value',            'INT16U',      'r'),
    ],
    'temperature' : [
        ('enable',           'INT8U',       'r/w'),
        ('rate',             'INT32U',      'r/w'),
        ('sampleCount',      'INT8U',       'r/w'),
        ('dataFormat',       'INT8U',       'r/w'),
        ('Value',            'INT16S',      'r'),
    ],
    'pkgen' : [
        ('echo',             'INT32U',      'r/w'),
        ('numPackets',       'INT32U',      'w'),
        ('rate',             'INT32U',      'w'),
        ('packetSize',       'INT8U',       'w'),
        ('startPID',         'INT32U',      'w'),
    ],
}
