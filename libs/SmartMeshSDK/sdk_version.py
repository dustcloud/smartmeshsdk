#
# The version in this file is automatically updated by the release script.
#
# PLEASE DO NOT CHANGE THE SYNTAX OF THE VERSION VALUE
# 
VERSION = (1, 3, 0, 1)
BUILD_TIME = '$VER_TIMESTAMP'
BUILD_NAME = '$VER_BUILD_NAME'

def get_version_label():
    ver_str = '.'.join(str(v) for v in VERSION)
    if BUILD_NAME:
        ver_str += '-' + BUILD_NAME
    return '{0} (built {1})'.format(ver_str, BUILD_TIME)

# END OF FILE
