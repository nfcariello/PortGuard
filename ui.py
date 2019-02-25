from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Progressbar
import socket
import sqlite3
import sys
from datetime import datetime
from urllib.request import urlopen

window = Tk()
window.title("PortGuard")

window.geometry('500x500')

selected = IntVar()

bar = Progressbar(window, length=200)


def initial():
    connection()


def connection():
    global conn
    global cursor
    conn = sqlite3.connect('port_services.sqlite')
    cursor = conn.cursor()


def querysql(port_import):
    sql = "SELECT * FROM main.port_information WHERE port = {}".format(port_import)
    try:
        cursor.execute(sql)
        # res = cursor.fetchall()  # Get all matching entries
        res = cursor.fetchone()  # Get the first matching entry
        try:
            # return res
            for r in res:
                return r
            # print('SQL SUCCESSFUL')
        except:
            return 0
    except sqlite3.Error:
        conn.rollback()
        return -1


def get_wan_ip():
    # get ip from http://ipecho.net/plain as text
    try:
        wan_ip = urlopen('http://ipecho.net/plain').read().decode('utf-8')
        return wan_ip
    except:
        sys.exit('WAN Retrieval Failure')


def get_remote_server_ip():
    remoteServer = get_wan_ip()
    remoteServerIP = socket.gethostbyname(remoteServer)
    return remoteServerIP


def get_setting():
    sel = selected.get()
    return sel


def wanScan():
    remoteServerIP = get_remote_server_ip()

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
                if query == -1:
                    sys.exit('SQL Failed')
                elif query == 0:
                    query = 'None'

                openPorts += 1
                port_results.insert(INSERT, "Port {0}:   Open     Service: {1}\n".format(port_scan, query))
                print("Port {0}:   Open     Service: {1}".format(port_scan, query))
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


status_label = Label(window, text='Status')
ip_label = Label(window, text='IP:')
start_port_label = Label(window, text='Starting Port:')
end_port_label = Label(window, text='Ending Port:')

status_box = Entry(window,width=15)
ip_box = Entry(window,width=12)
start_port_box = Entry(window, width=5)
end_port_box = Entry(window, width=5)

status_box.grid(column=4, row=1, columnspan=2)
status_label.grid(column=3, row=1, sticky=W)
ip_label.grid(column=0, row=1, sticky=W)
ip_box.grid(column=1, row=1, columnspan=2)
start_port_label.grid(column=0, row=2, columnspan=2, sticky=W)
start_port_box.grid(column=2, row=2)
end_port_label.grid(column=3, row=2, columnspan=2, sticky=W)
end_port_box.grid(column=5, row=2)

lan_rad = Radiobutton(window, text='LAN', value=1, variable=selected)
wan_rad = Radiobutton(window, text='WAN', value=2, variable=selected)
cust_rad = Radiobutton(window, text='Custom', value=3, variable=selected)
lan_rad.grid(column=0, row=0, columnspan=2)
wan_rad.grid(column=2, row=0, columnspan=2)
cust_rad.grid(column=4, row=0, columnspan=2)
port_results = scrolledtext.ScrolledText(window, width=40, height=10)
port_results.grid(column=0, row=4, columnspan=6, rowspan=4)


def start():
    setting = get_setting()
    if setting == 1:
        print('LAN Search')
        port_results.insert(INSERT, 'LAN Search\n')
    elif setting == 2:
        print('WAN Search')
        port_results.insert(INSERT, 'WAN Search\n')
        wanScan()
    elif setting == 3:
        print('Custom IP')
        port_results.insert(INSERT, 'Custom IP\n')
    else:
        print('NOPE')


btn = Button(window, text="Scan", command=start)
btn.grid(column=2, row=3, columnspan=2)
connection()
window.mainloop()
