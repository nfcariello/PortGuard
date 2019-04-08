from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Progressbar
import socket
import sqlite3
import sys

import iptools as iptools
import requests
from datetime import datetime
from urllib.request import urlopen
import time
from tkinter.ttk import *

window = Tk()
window.title("PortGuard")

window.geometry('650x550')

selected = IntVar()

bar = Progressbar(window, length=400)

failure = 'FAILED'
running = 'RUNNING'
completed = 'COMPLETED'
ready = 'READY'


def connection():
    global conn
    global cursor
    conn = sqlite3.connect('port_services.sqlite')
    cursor = conn.cursor()


def querysql(port_import):
    sql = "SELECT DISTINCT * FROM main.port_information WHERE port = {}".format(port_import)
    try:
        cursor.execute(sql)
        res = cursor.fetchall()  # Get all matching entries
        # res = cursor.fetchone()  # Get the first matching entry
        try:
            return res
            # for r in res:
            #     print(r)
            #     return r
            # print('SQL SUCCESSFUL')
        except:
            return 0
    except sqlite3.Error:
        conn.rollback()
        return -1


# def startFun():
#     print("Enter the starting port: ")
#     global start
#     start = input()
#     if int(start) < 1 or int(start) > 65535:
#         print("Not an acceptable value")
#         startFun()
#
#
# def endFun():
#     print("Enter the ending port: ")
#     global end
#     end = input()
#     if int(end) < 1 or int(end) > 65535:
#         print("Not an acceptable value")
#         endFun()


def progress_math():
    sp = int(get_start_port_box())
    ep = int(get_end_port_box())

    frac = ep - sp + 1
    res = 100 / frac
    return res


def get_wan_ip():
    # get ip from http://ipecho.net/plain as text
    try:
        wan_ip = urlopen('http://ipecho.net/plain').read().decode('utf-8')
        return wan_ip
    except:
        return '0.0.0.0'


def get_remote_server_ip():
    remoteServer = get_wan_ip()
    remoteServerIP = socket.gethostbyname(remoteServer)
    return remoteServerIP


def get_setting():
    sel = selected.get()
    return sel


def set_ip_box(text):
    ip_box.delete(0, END)
    ip_box.insert(0, text)
    return


def get_start_port_box():
    sp = start_port_box.get()
    return sp


def get_end_port_box():
    ep = end_port_box.get()
    return ep


def set_start_port_box(text):
    start_port_box.delete(0, END)
    start_port_box.insert(0, text)
    return


def set_end_port_box(text):
    end_port_box.delete(0, END)
    end_port_box.insert(0, text)
    return


def set_status_box(text):
    enable_status_box()
    status_box.delete(0, END)
    status_box.insert(0, text)
    disable_status_box()
    return


def enable_status_box():
    status_box['state'] = 'normal'


def disable_status_box():
    status_box['state'] = 'disabled'


# TODO Catch cant reach host

def wan_scan(remoteServerIP, start, end):
    set_status_box(running)
    # Print a nice banner with information on which host we are about to scan
    ui_console.insert(INSERT, '*' * 60 + '\n')
    ui_console.insert(INSERT, "Please wait, scanning remote host " + remoteServerIP + '\n')
    # print("Please wait, scanning remote host", remoteServerIP)
    ui_console.insert(INSERT, "Scanning Port(s) " + str(start) + " through " + str(end) + '\n')
    # print("Scanning Port(s) " + str(start) + " through " + str(end))
    ui_console.insert(INSERT, '*' * 60 + '\n')
    # port_results.insert(INSERT, 'Port   Status  Service                  Protocol   Vulnerability\n')
    # port_results.insert(INSERT, '-' * 60 + '\n')
    ui_console.update()
    # print("-" * 60)

    # Check what time the scan started
    t1 = datetime.now()

    # Using the range function to specify ports (here it will scans all ports between 1 and 65535)
    res = progress_math()

    # We also put in some error handling for catching errors
    open_ports = 0
    try:
        for port_scan in range(int(start), int(end)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((remoteServerIP, port_scan))
            # cp_res = connected_ports(remoteServerIP, port_scan)
            bar['value'] += res
            bar.update()

            if result == 0:
                query = querysql(port_scan)
                if query == -1:
                    ui_console.insert(INSERT, 'SQL Failed\n')
                    set_status_box(failure)
                    return
                    # sys.exit('SQL Failed')
                elif query == 0:
                    query = 'None'

                open_ports += 1
                for r in query:
                    insert_into_tree(port_scan, r[0], r[2], r[3])
                    time.sleep(1)
                    ui_console.update()
                    # print(
                    #     'Port: {0}     Status: Open    Service: {1}              Protocol: {2}
                    # Vulnerability: {3}'.format(
                    #         port_scan, r[0], r[2], r[3]))
            sock.close()
        ui_console.insert(INSERT, 'COMPLETE')

    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        ui_console.insert(INSERT, 'Hostname could not be resolved. Exiting\n')
        set_status_box(failure)
        return
        # sys.exit()

    except socket.error:
        print("Couldn't connect to server")
        ui_console.insert(INSERT, 'Couldn\'t connect to server\n')
        set_status_box(failure)
        return
        # sys.exit()

    # Checking the time again
    t2 = datetime.now()

    # Calculates the difference of time, to see how long it took to run the script
    total = t2 - t1
    enable_inputs()
    set_status_box(completed)


# UI Components

status_label = Label(window, text='Status:')
ip_label = Label(window, text='IP:')
start_port_label = Label(window, text='Starting Port:')
end_port_label = Label(window, text='Ending Port:')

status_box = Entry(window, width=15, state='disabled')
ip_box = Entry(window, width=16)
start_port_box = Entry(window, width=5)
end_port_box = Entry(window, width=5)

status_box.grid(column=4, row=2, columnspan=2)
status_label.grid(column=3, row=2, sticky=W)
ip_label.grid(column=0, row=2, sticky=W)
ip_box.grid(column=1, row=2, columnspan=2)
start_port_label.grid(column=0, row=3, columnspan=2, sticky=W)
start_port_box.grid(column=2, row=3)
end_port_label.grid(column=3, row=3, columnspan=2, sticky=W)
end_port_box.grid(column=5, row=3)

lan_rad = Radiobutton(window, text='LAN', value=1, variable=selected)
wan_rad = Radiobutton(window, text='WAN', value=2, variable=selected)
cust_rad = Radiobutton(window, text='Custom', value=3, variable=selected)
lan_rad.grid(column=0, row=0, columnspan=2)
wan_rad.grid(column=2, row=0, columnspan=2)
cust_rad.grid(column=4, row=0, columnspan=2)
ui_console = scrolledtext.ScrolledText(window, width=85, height=5)
ui_console.grid(column=0, row=5, columnspan=6, rowspan=4)
port_results = Treeview(window)
port_results.grid(column=0, row=9, columnspan=6, rowspan=4)
bar.grid(column=0, row=15, columnspan=6)
port_results['columns'] = ('status', 'service', 'protocol', 'vulnerability')
port_results.heading("#0", text='Port', anchor='w')
port_results.column("#0", anchor="center", width=13)
port_results.heading('status', text='Status')
port_results.column('status', anchor='center', width=20)
port_results.heading('service', text='Service')
port_results.column('service', anchor='center', width=100)
port_results.heading('protocol', text='Protocol')
port_results.column('protocol', anchor='center', width=10)
port_results.heading('vulnerability', text='Vulnerability')
port_results.column('vulnerability', anchor='center', width=100)
port_results.grid(sticky=(N, S, W, E))


def connected_ports(ip, port):
    print("-Testing port connection from the internet to %s:%s..." % (ip, port))
    data = {
        'remoteHost': ip,
        'start_port': port,
        'end_port': port,
        'scan_type': 'connect',
        'normalScan': 'Yes',
    }

    output = requests.post('http://www.ipfingerprints.com/scripts/getPortsInfo.php', data=data)
    if 'open ' in output.text:
        return output
    else:
        print("port is closed.")
        return False


def insert_into_tree(port, service, protocol, vulnerability):
    port_results.insert('', 'end', text=port, values=('OPEN', service, protocol, vulnerability))


def check_ip(ip):
    if iptools.ipv4.validate_ip(ip):
        return 0
    else:
        return -1


def check_port(start_port, end_port):
    if start_port == '' or end_port == '':
        return -1
    else:
        if end_port < start_port:
            return -1
        else:
            if int(start_port) > 65535 or int(start_port) < 0:
                return -1
            else:
                if int(end_port) > 65535 or int(start_port) < 0:
                    return -1
                else:
                    return 0


# TODO Fix this so that you can't pass bad values

# TODO Make it so that the output dialog does not allow input


def start():
    i = ip_box.get()
    st = start_port_box.get()
    en = end_port_box.get()
    cp = check_port(st, en)
    cip = check_ip(i)

    # TODO Fix this it should be able accept any domain
    if cp == -1 | cip == -1:
        print('nope')
        return
    else:
        disable_inputs()
        wan_scan(i, st, en)


def start_setting():
    setting = get_setting()
    if setting == 1:
        print('LAN Search')
        # port_results.insert(INSERT, 'LAN Search\n')
    elif setting == 2:
        print('WAN Search')
        # port_results.insert(INSERT, 'WAN Search\n')
        ip = get_remote_server_ip()
        start = 1
        end = 65535
        set_ip_box(ip)
        set_start_port_box(start)
        set_end_port_box(end)
    elif setting == 3:
        print('Custom IP')
        # port_results.insert(INSERT, 'Custom IP\n')
    else:
        print('NOPE')


def cancel():
    print('Does nothing sorry :(')

    # TODO Implement cancel functionality


# TODO enable a CLEAR button and functionality

# TODO add a 'reset' for after a search

# TODO add a functionality after search to return results, (num of open ports, time took, risk calculated)

# TODO split the UI and port scanning into individual files

# TODO Implement the LAN functionality (with IP, Open Port, etc.) Basically adds a field

# TODO Simplify UI to just allow for the entering of the IP

# TODO Confirm that the program is actually scanning the external IP but I have a feeling it doesn't, I added a function that calls a PHP script but it slows down majorly

cancel = Button(window, text="Cancel", command=cancel, state='disabled')
cancel.grid(column=2, row=4, sticky=E, columnspan=2)

select = Button(window, text="Select", command=start_setting)
select.grid(column=2, row=1, columnspan=2)

scan = Button(window, text="Scan", command=start)
scan.grid(column=2, row=4, sticky=W, columnspan=2)


def disable_inputs():
    ip_box['state'] = 'disabled'
    start_port_box['state'] = 'disabled'
    end_port_box['state'] = 'disabled'
    scan['state'] = 'disabled'
    select['state'] = 'disabled'
    lan_rad['state'] = 'disabled'
    wan_rad['state'] = 'disabled'
    cust_rad['state'] = 'disabled'
    cancel['state'] = 'normal'


def enable_inputs():
    ip_box['state'] = 'normal'
    start_port_box['state'] = 'normal'
    end_port_box['state'] = 'normal'
    scan['state'] = 'normal'
    select['state'] = 'normal'
    lan_rad['state'] = 'normal'
    wan_rad['state'] = 'normal'
    cust_rad['state'] = 'normal'
    cancel['state'] = 'disabled'


connection()
set_status_box(ready)
window.mainloop()
