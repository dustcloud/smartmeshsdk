'''
Dynamic structures

Build classes from a description of their fields
'''

from collections import namedtuple
import struct
import inspect

# An object description is a (ordered) list of field descriptions
# TODO: describe valid types
# TODO: add enums
# TODO: add printing hook, default to str()

ApiStructField = namedtuple('ApiStructField', 'name type len')

# obj = [ { 'name': 'field_name', 'type': [int, array, boolean], 'len': l }, ]

def parse_field(field, data, index = 0):
    s = index
    e = index + field.len
    if field.type is 'array':
        desc = '{0}B'.format(field.len)
        val = list(struct.unpack(desc, data[s:e]))
    elif field.type is 'int' and field.len is 1:
        try:
            val = struct.unpack('B', data[s])[0]
        except TypeError:
            aByte = data[s]
            if not isinstance(aByte,int):
                aByte = ord(aByte)
            val = struct.unpack('B', bytes([aByte]))[0]
    elif field.type is 'int' and field.len is 2:
        val = struct.unpack('!H', data[s:e])[0]
    elif field.type is 'int' and field.len is 4:
        try:
        val = struct.unpack('!L', data[s:e])[0]
        except TypeError:
            aByte = data[s]
            anInt = data[s:e]
            if not isinstance(aByte,int):
                anInt = [ord(b) for b in data[s:e]]
            val = struct.unpack('!L', bytes(anInt))[0]
    elif field.type is 'boolean':
        val = ord(data[s]) == 1
        pass
    elif inspect.isclass(field.type):
        val = parse_obj(field.type, data, index)
    else:
        raise Exception('unknown field type: ' + field.type)
    return (e, val)

def parse_obj(obj_type, data, index = 0):
    'Parse an object given a class and a data string'
    obj_vals = {}
    if len(data[index:]) < obj_type.serialized_length:
        raise IndexError('expected at least %s bytes of input' % obj_type.serialized_length)
    for f in obj_type.fields:
        (index, val) = parse_field(f, data, index)
        obj_vals[f.name] = val
    return obj_type(**obj_vals)

def to_string(self):
    'Generate a pretty printed string'
    out = ''
    for f in self.fields:
        out += '%16s: %s\n' % (f.name, str(self.__getattribute__(f.name)))
    return out

def serialize(self):
    'Serialize the structure in its binary API format'
    resp = b''
    for f in self.fields:
        val = self.__getattribute__(f.name)
        if f.type is 'array':
            desc = '{0}B'.format(f.len)
            resp += struct.pack(desc, *val)
        elif f.type is 'int' and f.len is 1:
            resp += struct.pack('B', val)
        elif f.type is 'int' and f.len is 2:
            resp += struct.pack('!H', val)
        elif f.type is 'int' and f.len is 4:
            resp += struct.pack('!L', val)
        elif f.type is 'boolean':
            resp += struct.pack('B', val)
        elif inspect.isclass(f.type):
            resp += val.serialize()
        else:
            raise Exception('unknown field type: ' + f.type)
    return resp



class GenObjectFactory(object):
    'Generic Factory for creating record objects from a list of fields'
    def __init__(self):
        self.object_map = {}

    def add_object(self, obj_id, obj_type):
        self.object_map[obj_id] = obj_type
        
    def parse(self, obj_id, data, index = 0):
        if obj_id in self.object_map:
            return parse_obj(self.object_map[obj_id], data, index)
        else:
            return None
    
    # note: fields is an array because we need to preserve field ordering
    def synthesize(self, obj_name, fields, obj_id = None):
        'Create an API object class from its list of fields'
        field_names = ' '.join([f.name for f in fields])
        obj_type = namedtuple(obj_name, field_names)
        # add the object to the list of things we can parse
        if obj_id:
            self.add_object(obj_id, obj_type)
        # add some useful stuff to the object
        obj_type.serialized_length = sum(f.len for f in fields)
        obj_type.fields = fields
        obj_type.__str__ = to_string
        obj_type.serialize = serialize
        return obj_type

