try:
    from . import IpMoteConnectorClib
    IpMoteConnector = IpMoteConnectorClib
    print ('Note: using the C implementation of the IpMoteConnector connector')
except ImportError:
    from . import IpMoteConnectorInternal
