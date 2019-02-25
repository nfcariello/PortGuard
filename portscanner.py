import socket
import sqlite3
import sys
from datetime import datetime
from urllib.request import urlopen


# build a basic UI
# reccomendation

# subprocess.call('clear', shell=True)

# Ask for input



# print("Enter a remote host to scan: ")


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



# Printing the information to screen
# print('Scanning Completed in: ', total)
# print('Total Number of Open Ports: ', openPorts)

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
