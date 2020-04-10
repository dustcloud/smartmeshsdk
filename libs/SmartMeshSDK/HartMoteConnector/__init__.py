try:
    from . import HartMoteConnectorClib
    HartMoteConnector = HartMoteConnectorClib
    print ('Note: using the C implementation of the HartMoteConnector connector')
except ImportError:
    from . import HartMoteConnectorInternal
