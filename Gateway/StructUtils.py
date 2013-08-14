'''
Structure utilities

Build classes from a description of their fields
'''

from collections import namedtuple
import struct

# An object description is a (ordered) list of field descriptions
# TODO: describe valid types
# TODO: add enums
# TODO: add printing hook, default to str()

ApiStructField = namedtuple('ApiStructField', 'name type len')

# obj = [ { 'name': 'field_name', 'type': [int, array, boolean], 'len': l }, ]


def parse_field(field, data):
    index = 0
    if field.type is 'array':
        desc = '{0}B'.format(field.len)
        val = list(struct.unpack(desc, data[0:field.len]))
    elif field.type is 'int' :
      if field.len is 1:
        val = struct.unpack('B', data[0])[0]
      elif field.len is 2:
        val = struct.unpack('!H', data[0:2])[0]
      elif field.len is 4:
        val = struct.unpack('!I', data[0:4])[0]
    elif field.type is 'sint' :
      if field.len is 1:
        val = struct.unpack('b', data[0])[0]
      elif field.len is 2:
        val = struct.unpack('!h', data[0:2])[0]
      elif field.len is 4:
        val = struct.unpack('!i', data[0:4])[0]
    elif field.type is 'asn' :
        val = 0
        for i in list(struct.unpack('!5B', data[0:5])) :
            val = val * 256 + i
    elif field.type is 'boolean':
        val = ord(data[0]) == 1
        pass
    else:
        raise Exception('unknown field type:' + field.type)
    index = field.len
    return (index, val)

def parse(obj_type, data):
    obj_vals = {}
    index = 0
    # TODO: check length
    for f in obj_type.fields:
        if (len(data) > index) :
            (index_incr, val) = parse_field(f, data[index:])
        else :
            (index_incr, val) = (0, None)
        obj_vals[f.name] = val
        index += index_incr
    return obj_type(**obj_vals)

def parse_self(self, data):
    obj_vals = {}
    index = 0
    # TODO: check length
    for f in self.fields:
        if (len(data) > index) :
            (index_incr, val) = parse_field(f, data[index:])
        else :
            (index_incr, val) = (0, None)
        obj_vals[f.name] = val
        index += index_incr
    return self.__class__(**obj_vals)

def parse_array(typeArrayItem, data):
    res = []
    offset = 0
    while (len(data) - offset >= typeArrayItem.size):
        item = parse(typeArrayItem, data[offset : offset+typeArrayItem.size])
        if item:
            res.append(item)
        offset += typeArrayItem.size
    return res

def pair_to_string(name, val):
    if type(val) == list:
        return '%16s: %s\n' % (name, '-'.join(['%02X' % c for c in val]))
    else:
        return '%16s: %s\n' % (name, str(val))

def to_string(self):
    'Generate a pretty printed string'
    return ''.join([pair_to_string(f.name, self.__getattribute__(f.name))
                    for f in self.fields])

def serialize(self):
    'Serialize the structure in its binary API format'
    resp = ''
    for f in self.fields:
        val = self.__getattribute__(f.name)
        if f.type is 'array':
            desc = '{0}B'.format(f.len)
            resp += struct.pack(desc, *val)
        elif f.type is 'int' :
            if f.len is 1:
               resp += struct.pack('B', val)
            elif f.len is 2:
               resp += struct.pack('!H', val)
            elif f.len is 4:
               resp += struct.pack('!I', val)
        elif f.type is 'sint' :
            if f.len is 1:
               resp += struct.pack('b', val)
            elif f.len is 2:
               resp += struct.pack('!h', val)
            elif f.len is 4:
               resp += struct.pack('!i', val)
        elif f.type is 'boolean':
            resp += struct.pack('B', val)
        elif f.type is 'asn' :
            v = val
            ar = [0, 0, 0, 0, 0]
            for i in range(0, 5) :
               l[4-i] = v % 256
               v = v / 256
            resp += struct.pack('5B', *v)
        else:
            raise Exception('unknown field type:' + field.type)
    return resp


# TODO: instead of passing in an array of field structs, 
# build the array from a dict
def synthesize(obj_name, fields):
    'Create an API object class from its list of fields'
    field_names = ' '.join([f.name for f in fields])
    obj_type = namedtuple(obj_name, field_names)
    # add some useful stuff
    obj_type.fields = fields
    # TODO: somehow parse needs to be a class method (really a factory)
    #obj_type.parse = parse
    #obj_type.parse_s = parse_self
    obj_type.__str__ = to_string
    obj_type.serialize = serialize
    obj_type.size = sum(f.len for f in fields)
    return obj_type
