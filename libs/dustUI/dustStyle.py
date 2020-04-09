#!/usr/bin/python

import platform
from builtins import input
class dustStyle(object):
    
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
    COLOR_WARNING                      = 'orange'
    COLOR_WARNING_NOTWORKING           = 'orange'
    COLOR_WARNING_FORMATTING           = 'yellow'
    COLOR_NOERROR                      = 'green'
    
    # text field widths
    TEXTFIELD_ENTRY_LENGTH_DEFAULT     = 8
    TEXTFIELD_ENTRY_LENGTH_MAX         = 35

    # font (only customize font on Windows)
    if platform.system() in ['Windows']:
        FONT_HEADER     = ('Helvetica','8','bold')
        FONT_BODY       = ('Helvetica','8')
        FONT_STATION    = ('Helvetica','16','bold') 
    else:
        FONT_HEADER     = 'TkDefaultFont'
        FONT_BODY       = 'TkDefaultFont'

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        input("No sample app. Press enter to close.")

if __name__ == '__main__':
    exampleApp()