'''
The FilterExpr class implements the filter() method for easily applying
whitelist and blacklist operations to fields of an object.

If a whitelist is defined, then filter() only returns True for objects that
match the whitelist. Otherwise, if a blacklist is defined, then filter()
returns True for any object that does not match the blacklist. If both a
whitelist and a blacklist are defined, then filter() returns True IF the
object matches the whitelist and doesn't match the blacklist.

Currently, matching the whitelist means matching any single attribute on the
whitelist.
TODO: allow option to select whether whitelist must match ALL attributes or ANY

TODO: allow filters to be chained


>>> f = FilterExpr()
>>> f.whitelist_attrib('dest_port', 0xF0B2)  # whitelist dest_port == 0xF0B2
>>> class Whatever(object):
...    def __init__(self, p):
...        self.dest_port = p
...
>>> good_obj = Whatever(0xF0B2)
>>> bad_obj = Whatever(1792)
>>> f.filter(good_obj)
True
>>> f.filter(bad_obj)
False
>>> # Matching MAC addresses is special
>>> another_f = FilterExpr()
>>> another_f.blacklist_mac([0xA0, 0x11])
>>> class Whatever2(object):
...    def __init__(self, m):
...        self.mac = m
...
>>> good_obj = Whatever2([0, 1, 2, 0, 0, 17, 1, 2])
>>> bad_obj = Whatever2([0, 1, 2, 0, 0, 17, 0xA0, 0x11])
>>> another_f.filter(good_obj)
True
>>> another_f.filter(bad_obj)
False

'''

def ends_with(full, exp):
    return full[-len(exp):] == exp


class FilterExpr(object):
    def __init__(self):
        self.mac_whitelist = []
        self.mac_blacklist = []

        self.attrib_whitelist = {}
        self.attrib_blacklist = {}

    def whitelist_mac(self, mac):
        'Append the mac to the whitelist'
        self.mac_whitelist += [mac]

    def blacklist_mac(self, mac):
        'Append the mac to the blacklist'
        self.mac_blacklist += [mac]

    
    def whitelist_attrib(self, attrib, val):
        'Append a whitelist value to an arbitrary attribute'
        self.attrib_whitelist.setdefault(attrib, []).append(val)
        
    def blacklist_attrib(self, attrib, val):
        'Append a blacklist value to an arbitrary attribute'
        self.attrib_blacklist.setdefault(attrib, []).append(val)

        
    def filterByMac(self, obj):
        result = True
        # if there is a whitelist, default to returning False
        if len(self.mac_whitelist):
            result = False
            for m in self.mac_whitelist:
                if ends_with(obj.mac, m):
                    return True

        if len(self.mac_blacklist):
            for m in self.mac_blacklist:
                if ends_with(obj.mac, m):
                    return False

        return result

    def filterByAttribs(self, obj):
        result = True
        # if there is a whitelist, default to returning False
        try: 
            if len(self.attrib_whitelist):
                result = False
                for attr, valary in list(self.attrib_whitelist.items()):
                    for val in valary:
                        if obj.__dict__[attr] == val:
                            return True
            
            if len(self.attrib_blacklist):
                for attr, valary in list(self.attrib_blacklist.items()):
                    for val in valary:
                        if obj.__dict__[attr] == val:
                            return False

        except KeyError:
            result = False

        return result

    def filter(self, obj):
        'Return whether or not an object matches the filter'
        return self.filterByMac(obj) and self.filterByAttribs(obj)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
