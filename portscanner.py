import socket
import sqlite3
import sys
from datetime import datetime
from urllib.request import urlopen


# subprocess.call('clear', shell=True)

# Ask for input


def connection():
    global conn
    global cursor
    conn = sqlite3.connect('port_services.sqlite')
    cursor = conn.cursor()


def querysql(port_import):
    sql = "SELECT * FROM main.port_information WHERE port = {}".format(port_import)
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        try:
            for r in res:
                return r
            print('SQL SUCCESSFUL')
        except:
            return 0
    except sqlite3.Error:
        conn.rollback()
        print('SQL FAILED')


def get_wan_ip():
    # get ip from http://ipecho.net/plain as text
    wan_ip = urlopen('http://ipecho.net/plain').read().decode('utf-8')
    return wan_ip


connection()
print("Enter a remote host to scan: ")
remoteServer = get_wan_ip()
remoteServerIP = socket.gethostbyname(remoteServer)


def startFun():
    print("Enter the starting port: ")
    global start
    start = input()
    if int(start) < 1 or int(start) > 65535:
        print("Not an acceptable value")
        startFun()


def endFun():
    print("Enter the ending port: ")
    global end
    end = input()
    if int(end) < 1 or int(end) > 65535:
        print("Not an acceptable value")
        endFun()


# Accept starting port
# startFun()
# Accept ending port
# endFun()

start = 1
end = 65535

# Print a nice banner with information on which host we are about to scan
print("-" * 60)
print("Please wait, scanning remote host", remoteServerIP)
print("Scanning Port(s) " + str(start) + " through " + str(end))
print("-" * 60)

# Check what time the scan started
t1 = datetime.now()

# Using the range function to specify ports (here it will scans all ports between 1 and 65535)

# We also put in some error handling for catching errors
openPorts = 0
try:
    for port_scan in range(int(start), int(end)):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((remoteServerIP, port_scan))
        if result == 0:
            query = querysql(port_scan)
            openPorts += 1
            print("Port {0}: 	            Open        Service: {1}".format(port_scan, query))
        sock.close()

except socket.gaierror:
    print('Hostname could not be resolved. Exiting')
    sys.exit()

except socket.error:
    print("Couldn't connect to server")
    sys.exit()

# Checking the time again
t2 = datetime.now()

# Calculates the difference of time, to see how long it took to run the script
total = t2 - t1

# Printing the information to screen
print('Scanning Completed in: ', total)
print('Total Number of Open Ports: ', openPorts)

# import logging
# import scapy.config
# import scapy.layers.l2
# import scapy.route
# import socket
# import math
# import errno
#
# logging.basicConfig(format='%(asctime)s %(levelname)-5s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
#
# def long2net(arg):
#     if (arg <= 0 or arg >= 0xFFFFFFFF):
#         raise ValueError("illegal netmask value", hex(arg))
#     return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))
#
#
# def to_CIDR_notation(bytes_network, bytes_netmask):
#     network = scapy.utils.ltoa(bytes_network)
#     netmask = long2net(bytes_netmask)
#     net = "%s/%s" % (network, netmask)
#     if netmask < 16:
#         logger.warn("%s is too big. skipping" % net)
#         return None
#
#     return net
#
#
# def scan_and_print_neighbors(net, interface, timeout=5):
#     logger.info("arping %s on %s" % (net, interface))
#     try:
#         ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=True)
#         for s, r in ans.res:
#             line = r.sprintf("%Ether.src%  %ARP.psrc%")
#             try:
#                 hostname = socket.gethostbyaddr(r.psrc)
#                 line += " " + hostname[0]
#             except socket.herror:
#                 # failed to resolve
#                 pass
#             logger.info(line)
#     except socket.error as e:
#         if e.errno == errno.EPERM:  # Operation not permitted
#             logger.error("%s. Did you run as root?", e.strerror)
#         else:
#             raise
#
#
# if __name__ == "__main__":
#     for network, netmask, _, interface, address, _ in scapy.config.conf.route.routes:
#
#         # skip loopback network and default gw
#         if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
#             continue
#
#         if netmask <= 0 or netmask == 0xFFFFFFFF:
#             continue
#
#         net = to_CIDR_notation(network, netmask)
#
#         if net:
#             scan_and_print_neighbors(net, interface)
