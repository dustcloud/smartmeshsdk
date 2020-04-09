"""XML utility functions"""

from xml.dom.minidom import parseString


def xml_obj_to_dict(xml_obj):
    attrs = {}
    ch_node = xml_obj.firstChild
    while ch_node:
        # look for ELEMENT_NODEs
        if ch_node.nodeType == ch_node.ELEMENT_NODE:
            #print 'Reading', ch_node.nodeName
            n = str(ch_node.nodeName)
            v = ''
            # iterate through the children of the current node either
            # accumulating multiple child text nodes into a single string, or
            # recursing to build a dict of child elements
            ch2_node = ch_node.firstChild
            while ch2_node:
                if ch2_node.nodeType in [ch_node.TEXT_NODE, ch_node.CDATA_SECTION_NODE]:
                    v += str(ch2_node.nodeValue)

                # if the child is an element, then build a dict
                elif ch2_node.nodeType == ch_node.ELEMENT_NODE:
                    v = xml_obj_to_dict(ch_node)
                    break

                ch2_node = ch2_node.nextSibling

            # populate the attributes dict with the value
            # create a list of values if the child name already exists
            if n in attrs:
                if not type(attrs[n]) is list:
                    attrs[n] = [attrs[n]]
                attrs[n].append(v)
            else:
                attrs[n] = v
            if ch_node.hasAttributes():
                for name, val in list(ch_node.attributes.items()):
                    attr_name = n + name.capitalize()
                    attrs[attr_name] = val

        ch_node = ch_node.nextSibling
    
    return attrs


def parse_xml_obj(xml_str, base_element, fields = None):
    xml_doc = parseString(xml_str)
    obj_docs = xml_doc.getElementsByTagName(base_element)
    # parse each found object into a dict of fields
    obj_dicts = []
    for obj_doc in obj_docs:
        obj_dicts.append(xml_obj_to_dict(obj_doc))
        if fields:
            # TODO: filter dict for requested fields
            pass
    return obj_dicts

def _dict_to_xml(inpDict, outList) :
    for k in inpDict :
        outList.append('<{0}>'.format(k))
        if inpDict[k] :
            if isinstance(inpDict[k], dict) :
                _dict_to_xml(inpDict[k], outList)
            else :
                outList.append('{0}'.format(inpDict[k]))
        outList.append('</{0}>'.format(k))

def dict_to_xml(inpDict, prefix = None) :
    outList = []
    if prefix :
        outList.append(''.join(['<{0}>'.format(p) for p in prefix]))
    _dict_to_xml(inpDict, outList)
    if prefix :
        outList.append(''.join(['</{0}>'.format(p) for p in reversed(prefix)]))
    return ''.join([l for l in outList])

def list_to_xml(inpList, el_tag, prefix = None):
    outList = []
    if prefix :
        outList.append(''.join(['<{0}>'.format(p) for p in prefix]))
    for el in inpList:
        outList.append('<{0}>{1}</{0}>'.format(el_tag, el))
    if prefix :
        outList.append(''.join(['</{0}>'.format(p) for p in reversed(prefix)]))
    return ''.join(outList)
