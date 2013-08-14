#!/usr/bin/python

import platform

class dustStyle(object):
    '''
    \ingroup guiLib
    
    \brief Colors used in the different GUI applications.
    '''
    
    # colors
    COLOR_BG                           = '#ffffff'
    
    COLOR_PRIMARY1                     = '#003745'
    COLOR_PRIMARY2                     = '#00aeda'
    COLOR_PRIMARY2_LIGHT               = '#11cfff'
    
    COLOR_SECONDARY1                   = '#00456b'
    COLOR_SECONDARY2                   = '#00535e'
    COLOR_SECONDARY3                   = '#008b98'
    COLOR_SECONDARY4                   = '#008aad'
    
    COLOR_ERROR                        = 'red'
    COLOR_WARNING_NOTWORKING           = 'orange'
    COLOR_WARNING_FORMATTING           = 'yellow'
    COLOR_NOERROR                      = 'green'
    
    # text field widths
    TEXTFIELD_ENTRY_LENGTH_DEFAULT     = 8
    TEXTFIELD_ENTRY_LENGTH_MAX         = 35

    # font (only customize font on Windows)
    if platform.system() in ['Windows']:
        FONT_HEADER = ('Helvetica','8','bold')
        FONT_BODY   = ('Helvetica','8')
    else:
        FONT_HEADER = 'TkDefaultFont'
        FONT_BODY   = 'TkDefaultFont'

        
def formatMacAddress(mac):
    return '-'.join("%.2x"%b for b in mac)