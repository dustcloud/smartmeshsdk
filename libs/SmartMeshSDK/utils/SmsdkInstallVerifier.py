#!/usr/bin/python

PYTHON   = 'Python'
PYSERIAL = 'PySerial'
PYWIN32  = 'PyWin32'
WEBPY    = 'WebPy'

REQUIRED_PYTHON_MAJOR = 2
REQUIRED_PYTHON_MINOR = 6

#======================== private =========================================

def _verifyPython():
    import sys
    import platform

    output = []
    
    # verify Python version running -- use the tuple format for compatibility,
    # .major, .minor, etc are only present in 2.7
    major   = sys.version_info[0]
    minor   = sys.version_info[1]
    micro   = sys.version_info[2]
    output += [
        "You are running Python {0}.{1}.{2} on platform {3}, {4}".format(
            major,
            minor,
            micro,
            platform.platform(),
            platform.machine()
        )
    ]
    
    # is that enough?
    if major==REQUIRED_PYTHON_MAJOR and minor>=REQUIRED_PYTHON_MINOR:
        goodToGo = True
    else:
        output += ["You need at least Python {0}.{1}".format(REQUIRED_PYTHON_MAJOR,REQUIRED_PYTHON_MINOR)]
        goodToGo = False
        
    return (goodToGo,'\n'.join(output))

def _verifyPyserial():
    output = []
    pyserial_needed = False
    
    try:
        import serial
        goodToGo = True
        output +=  ["You have PySerial {0}".format(serial.VERSION)]
    except ImportError:
        goodToGo = False
        pyserial_needed = True

    if pyserial_needed:
        output +=  ["You need to install PySerial:"]
        output +=  [" - information http://pyserial.sourceforge.net/"]
        try:
            import easy_install
            output +=  [" - install with 'easy_install pyserial'"]
        except:
            output +=  [" - download pyserial-2.5.win32.exe from http://sourceforge.net/projects/pyserial/files/pyserial/2.5/"]
        
    return (goodToGo,'\n'.join(output))

def _verifyPywin32():
    import os

    if not os.name in ['nt']:
        return (True, 'PyWin32 is not used on non-Windows systems.')
    
    output = []
    pywin32_needed = False

    try:
        import pywintypes
        import win32api
        goodToGo = True
        try:
            fixed_file_info = win32api.GetFileVersionInfo(win32api.__file__, '\\')
            pywin32_ver = fixed_file_info['FileVersionLS'] >> 16
            output += ["You have PyWin32 build {0}".format(pywin32_ver)]
        except pywintypes.error:
            # pypiwin32 can not detect the version resource in its own win32api file
            output += ["PyWin32 is installed via pypiwin32, but pypiwin32 cannot find the version"]
    except ImportError:
        goodToGo = False
        pywin32_needed = True

    if pywin32_needed:
        output +=  ["You need to install PyWin32:"]
        output +=  [" - information http://sourceforge.net/projects/pywin32/"]
        output +=  [" - download and install the latest release for your Python version from http://sourceforge.net/projects/pywin32/files/pywin32/"]
        
    return (goodToGo,'\n'.join(output))

def _verifyWebPy():
    output = []
    webpy_needed = False
    
    try:
        import web
        goodToGo = True
        output +=  ["You have web.py intalled"]
    except ImportError:
        goodToGo = False
        webpy_needed = True

    if webpy_needed:
        output +=  ["You need to install web.py:"]
        output +=  [" - information http://webpy.org/"]
        try:
            import easy_install
            output +=  [" - install with 'easy_install web'"]
        except:
            output +=  [" - follow installation procedure at http://webpy.org/install"]
        
    return (goodToGo,'\n'.join(output))


ComponentTests = { PYTHON:   _verifyPython,
                   PYSERIAL: _verifyPyserial,
                   PYWIN32:  _verifyPywin32,
                   WEBPY:    _verifyWebPy, }

#======================== public ==========================================

def verifyComponents(elementsToTest):
    for elem in elementsToTest:
        try:
            (goodToGo,reason) = ComponentTests[elem]()
        except KeyError:
            goodToGo = False
            reason = 'error: unknown component to verify: '+str(elem)

        if goodToGo==False:
            return (goodToGo,reason)

    # HACK: InstallTest calls this with one component at a time, so we return the
    # last (only) reason which contains a message about the current version.
    # Other components mostly care about the goodToGo result, and only look at
    # the reason on failure.
    return (True, reason)
