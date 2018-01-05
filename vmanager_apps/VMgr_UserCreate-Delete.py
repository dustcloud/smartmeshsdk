#!/usr/bin/python
'''
Basic example. This script queries the manager and prints out the current users,
then creates a user named user1 (if it does not already exist), then deletes
it again. Note how these settings are done by writing to the "Config" space,
then doing a "reload" to activate.
'''

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'libs'))
    sys.path.insert(0, os.path.join(here, '..', 'external_libs'))

#============================ imports =========================================

import urllib3
import traceback
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException
from VManagerSDK.vmanager              import UserWriteConfig

#============================ defines =========================================

DFLT_VMGR_HOST          = "127.0.0.1"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_UserCreate-Delete Example (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0} ): '.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST

    # log in as user "dust"
    config = Configuration()
    config.username     = 'dust'
    config.password     = 'dust'
    config.verify_ssl   = False
    
    if os.path.isfile(certifi.where()):
        config.ssl_ca_cert  = certifi.where()
    else:
        config.ssl_ca_cert = os.path.join(os.path.dirname(sys.executable), "cacert.pem")

    # initialize the VManager Python library
    voyager = VManagerApi(host=mgrhost)

    # ==== Create a new user in configuration memory if doesn't already exist
    userName       = "user1"
    userExists     = False
    # read the list of users first (in Config area) to see if it already exists
    print "\n The current users in Config are ..."
    myUsers = voyager.usersApi.get_config_users()
    for x in myUsers.users:
        print '    {0}'.format(x.user_id)
        if x.user_id == userName:
            userExists = True

    # create the new user if not already there
    if not userExists:
        print '\n Creating a new user called {0}\n'.format(userName)
        userConfigbody = UserWriteConfig()
        userConfigbody.description     = "NewUser1"
        userConfigbody.password        = "secretpw"
        userConfigbody.privilege       = "user"
        voyager.usersApi.add_config_user(userName, userConfigbody)

    # execute a reload to activate any new changes made in Config area
    voyager.configApi.reload_config()

    # read the list of users in "Active" area
    print "\n The current Active users are ..."
    myActiveUsers = voyager.usersApi.get_users()
    for x in myActiveUsers.users:
        print ('    {0}'.format(x.user_id))
    
    # Delete the user from the system (Config area then reload)
    print "\n Deleting the user we just created"
    voyager.usersApi.delete_config_user(userName)
    voyager.configApi.reload_config()

    print "\n The current Active users are now ..."
    myActiveUsers = voyager.usersApi.get_users()
    for x in myActiveUsers.users:
        print ('    {0}'.format(x.user_id))

    print 'Script ended normally'
    
except:
    traceback.print_exc()
    print ('\n Script ended with an error.')
    sys.exit()
