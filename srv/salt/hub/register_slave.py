#!{{grains['pythonexecutable']}}

import sys
import time
import socket
import xmlrpc.client

if len(sys.argv) != 5:
    print("Usage: register_slave.py <USERNAME> <PASSWORD> <MASTER FQDN> <SLAVE FQDN>")
    sys.exit(1)

MANAGER_URL = "http://{}/rpc/api".format(sys.argv[3])

# ensure Tomcat is up

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for _ in range(10):
    try:
        sock.connect_ex(sys.argv[3], 443)
        break
    except:
        time.sleep(3)

client = xmlrpc.client.Server(MANAGER_URL, verbose=0)

session_key = None
attempts = 10
while session_key is None and attempts > 0:
    try:
        session_key = client.auth.login(sys.argv[1], sys.argv[2])
    except xmlrpc.client.ProtocolError:
        time.sleep(3)
        attempts -= 1

try:
    previous_slave = client.sync.slave.getSlaveByName(session_key, sys.argv[4])
    client.sync.slave.delete(session_key, previous_slave["id"])
    print("Pre-existing Slave deleted.")
except:
    pass

slave = client.sync.slave.create(session_key, sys.argv[4], True, True)

print("Slave added to this Master.")

orgs = client.org.listOrgs(session_key)
result = client.sync.slave.setAllowedOrgs(session_key, slave["id"], [org["id"] for org in orgs])
if result != 1:
    print("Got error %d on setAllowedOrgs" % result)
    sys.exit(1)

print("All orgs exported.")

print("Done.")