import socket
import sqlite3
import time
import tkinter as tk
from datetime import datetime
from tkinter import *
from urllib.request import urlopen
import map_network as map_n
import iptools
import requests
from PIL import ImageTk, Image
import tkinter.ttk as ttk

LARGE_FONT = ("Verdana", 25)
background_color = '#3a3e44'

failure = 'FAILED'
running = 'RUNNING'
completed = 'COMPLETED'
ready = 'READY'
getting_devices = 'GETTING DEVICES'


def get_wan_ip():
    # get ip from http://ipecho.net/plain as text
    try:
        wan_ip = urlopen('http://ipecho.net/plain').read().decode('utf-8')
        return wan_ip
    except:
        return '0.0.0.0'


def get_remote_server_ip():
    remote_server = get_wan_ip()
    remote_server_ip = socket.gethostbyname(remote_server)
    return remote_server_ip


class MainApplication(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.configure(background='#3a3e44')


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        load = Image.open("portguard.png")
        load = load.resize((350, 350), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render, borderwidth=0, highlightthickness=0, fg=background_color, padx=0, pady=0)
        img.image = render
        img.pack()

        button = tk.Button(self, text="Scan My Network", font=LARGE_FONT,
                           command=lambda: controller.show_frame(PageOne))
        button.pack(pady='20', padx='20')

        button2 = tk.Button(self, text="Scan My External IP", font=LARGE_FONT,
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack(pady='20', padx='20')


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Scan My Network", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        bar = ttk.Progressbar(self, length=500)

        iplist = []

        def reset_ui_for_search():
            bar['value'] = 0
            port_results.delete(*port_results.get_children())

        def querysql(port_import):
            # Prepare SQL Statement to select the port information
            sql = "SELECT DISTINCT * FROM main.port_information WHERE port = {}".format(port_import)
            # Define the connection to the database for the vulnerabilities
            conn = sqlite3.connect('port_services.sqlite')
            # Set a cursor for the connection
            cursor = conn.cursor()
            # Try to execute the SQL statement in the database
            try:
                cursor.execute(sql)
                # Fetch all results from the database
                result = cursor.fetchall()  # Get all matching entries
                # res = cursor.fetchone()  # Get the first matching entry
                try:
                    # Return the result
                    return result
                except:
                    return 0
            except sqlite3.Error:
                conn.rollback()
                return -1

        def insert_into_tree(ip, port, service, protocol, vulnerability):
            port_results.insert('', 'end', text=ip, values=(port, 'OPEN', service, protocol, vulnerability))

        def insert_into_network_devices(ip):
            ip_devices.insert('', 'end', text=ip, values=('',))

        def check_port(start_port, end_port):
            if start_port == '' or end_port == '':
                return -1
            elif end_port < start_port:
                return -1
            elif int(start_port) > 65535 or int(start_port) < 0:
                return -1
            elif int(end_port) > 65535 or int(start_port) < 0:
                return -1
            else:
                return 0

        def disable_inputs():
            ip_box['state'] = 'disabled'
            start_port_box['state'] = 'disabled'
            end_port_box['state'] = 'disabled'
            start_single_scan['state'] = 'disabled'
            start_multi_scan['state'] = 'disabled'

        def enable_inputs():
            ip_box['state'] = 'normal'
            start_port_box['state'] = 'normal'
            end_port_box['state'] = 'normal'
            start_single_scan['state'] = 'normal'
            start_multi_scan['state'] = 'normal'

        def start_single_search():
            reset_ui_for_search()
            i = ip_box.get()
            st = start_port_box.get()
            en = end_port_box.get()
            cp = check_port(st, en)
            cip = check_ip(i)

            if cp == -1 | cip == -1:
                return
            else:
                disable_inputs()
                set_status_box(running)
                lan_scan(i, st, en)
                set_status_box(completed)
                enable_inputs()

        def start_multi_search():
            reset_ui_for_search()
            start = start_port_box.get()
            end = end_port_box.get()
            disable_inputs()
            set_status_box(running)
            iterate_lan_scan(iplist, start, end)
            set_status_box(completed)
            enable_inputs()

        def iterate_lan_scan(ip_list, start, end):
            print(ip_list)
            for ip in ip_list:
                lan_scan(ip, start, end)

        def set_start_port_box(text):
            start_port_box.delete(0, END)
            start_port_box.insert(0, text)
            return

        def set_end_port_box(text):
            end_port_box.delete(0, END)
            end_port_box.insert(0, text)
            return

        def enable_status_box():
            status_box['state'] = 'normal'

        def disable_status_box():
            status_box['state'] = 'disabled'

        def set_status_box(text):
            enable_status_box()
            status_box.delete(0, END)
            status_box.insert(0, text)
            disable_status_box()
            return

        def insert_network_devices():
            set_status_box(getting_devices)
            get_internal_ip()
            ips = get_ip_list()
            iplist.extend(ips)
            for ip in ips:
                insert_into_network_devices(ip)
            set_status_box(ready)

        def check_ip(ip):
            if iptools.ipv4.validate_ip(ip):
                return 0
            else:
                return -1

        def get_ip_list():
            ips = map_n.map_network()
            return ips

        def lan_scan(remote_ip, start, end):
            t1 = datetime.now()
            res = progress_math(start, end)
            open_ports = 0
            try:
                for port_scan in range(int(start), int(end)):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((remote_ip, port_scan))
                    bar['value'] += res
                    bar.update()

                    if result == 0:
                        query = querysql(port_scan)
                        if query == -1:
                            set_status_box(failure)
                            return
                        elif query == 0:
                            query = 'None'
                        open_ports += 1
                        for r in query:
                            insert_into_tree(remote_ip, port_scan, r[0], r[2], r[3])
                            time.sleep(1)
                    sock.close()
                bar['value'] += res

            except socket.gaierror:
                print('Hostname could not be resolved. Exiting')
                set_status_box(failure)
                return

            except socket.error:
                print("Couldn't connect to server")
                set_status_box(failure)
                return

            t2 = datetime.now()

            total = t2 - t1
            print(total)

        def progress_math(start_port, end_port):
            frac = int(end_port) - int(start_port) + 1
            res = 100 / frac
            return res

        def set_ip_box(ip):
            ip_box.delete(0, END)
            ip_box.insert(0, ip)
            return

        def get_internal_ip():
            ip = map_n.get_my_ip()
            set_ip_box(ip)
            set_start_port_box(1)
            set_end_port_box(65535)

        return_home = tk.Button(self, text="Back to Home", pady='8', command=lambda: controller.show_frame(StartPage))
        return_home.pack()

        get_my_internal_ip = tk.Button(self, text="Get My Internal IP", pady='8', command=get_internal_ip)

        ip_box = Entry(self, width=16)
        start_port_box = Entry(self, width=5)
        end_port_box = Entry(self, width=5)
        ip_label = Label(self, text='IP:')
        start_port_label = Label(self, text='Starting Port:')
        end_port_label = Label(self, text='Ending Port:')

        ip_label.place(x=220, y=101)
        ip_box.place(x=250, y=100)
        get_my_internal_ip.place(x=260, y=140)

        start_port_label.place(x=240, y=191)
        start_port_box.place(x=340, y=190)
        end_port_label.place(x=240, y=231)
        end_port_box.place(x=340, y=230)

        status_box = Entry(self, width=15, state='disabled')
        status_label = Label(self, text='Status:')
        status_box.place(x=490, y=80)
        status_label.place(x=490, y=50)

        set_status_box(ready)

        start_multi_scan = tk.Button(self, text="Start Multi Scan", pady='8', command=start_multi_search)
        start_multi_scan.place(x=180, y=280)

        start_single_scan = tk.Button(self, text="Start Single Scan", pady='8', command=start_single_search)
        start_single_scan.place(x=380, y=280)

        ip_devices_label = Label(self, text='Network Devices:')
        ip_devices_label.place(x=10, y=10)

        ip_devices = ttk.Treeview(self)
        ip_devices.place(x=10, y=35)
        ip_devices['columns'] = ('scanned',)
        ip_devices.heading("#0", text='IP', anchor='w')
        ip_devices.column("#0", anchor="center", width=120)
        ip_devices.heading('scanned', text='Scan?')
        ip_devices.column('scanned', anchor='center', width=40)

        ip_devices_get = Button(self, text="Get Network Devices", pady='8', command=insert_network_devices)
        ip_devices_get.place(x=20, y=250)

        port_results = ttk.Treeview(self)
        port_results.pack(fill=X, padx='7', side='bottom')
        port_results['columns'] = ('port', 'status', 'service', 'protocol', 'vulnerability')
        port_results.heading("#0", text='IP', anchor='w')
        port_results.column("#0", anchor="center", width=60)
        port_results.heading('port', text='Port')
        port_results.column('port', anchor='center', width=2)
        port_results.heading('status', text='Status')
        port_results.column('status', anchor='center', width=4)
        port_results.heading('service', text='Service')
        port_results.column('service', anchor='center', width=90)
        port_results.heading('protocol', text='Protocol')
        port_results.column('protocol', anchor='center', width=4)
        port_results.heading('vulnerability', text='Vulnerability')
        port_results.column('vulnerability', anchor='center', width=100)
        bar.pack(side='bottom', after=port_results, pady='5')


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Scan My External IP", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        bar = ttk.Progressbar(self, length=500)

        def reset_ui_for_search():
            bar['value'] = 0
            port_results.delete(*port_results.get_children())

        def querysql(port_import):
            # Prepare SQL Statement to select the port information
            sql = "SELECT DISTINCT * FROM main.port_information WHERE port = {}".format(port_import)
            # Define the connection to the database for the vulnerabilities
            conn = sqlite3.connect('port_services.sqlite')
            # Set a cursor for the connection
            cursor = conn.cursor()
            # Try to execute the SQL statement in the database
            try:
                cursor.execute(sql)
                # Fetch all results from the database
                result = cursor.fetchall()  # Get all matching entries
                # res = cursor.fetchone()  # Get the first matching entry
                try:
                    # Return the result
                    return result
                except:
                    return 0
            except sqlite3.Error:
                conn.rollback()
                return -1

        def connected_ports(ip, port):
            data = {
                'remoteHost': ip,
                'start_port': port,
                'end_port': port,
                'scan_type': 'connect',
                'normalScan': 'Yes',
            }

            output = requests.post('http://www.ipfingerprints.com/scripts/getPortsInfo.php', data=data)
            if 'open ' in output.text:
                return 0
            else:
                return -1

        def check_ip(ip):
            if iptools.ipv4.validate_ip(ip):
                return 0
            else:
                return -1

        def insert_into_tree(port, service, protocol, vulnerability):
            port_results.insert('', 'end', text=port, values=('OPEN', service, protocol, vulnerability))

        def check_port(start_port, end_port):
            if start_port == '' or end_port == '':
                return -1
            elif end_port < start_port:
                return -1
            elif int(start_port) > 65535 or int(start_port) < 0:
                return -1
            elif int(end_port) > 65535 or int(start_port) < 0:
                return -1
            else:
                return 0

        def disable_inputs():
            ip_box['state'] = 'disabled'
            start_port_box['state'] = 'disabled'
            end_port_box['state'] = 'disabled'
            start_scan['state'] = 'disabled'

        def enable_inputs():
            ip_box['state'] = 'normal'
            start_port_box['state'] = 'normal'
            end_port_box['state'] = 'normal'
            start_scan['state'] = 'normal'

        def start():
            reset_ui_for_search()
            i = ip_box.get()
            st = start_port_box.get()
            en = end_port_box.get()
            cp = check_port(st, en)
            cip = check_ip(i)

            if cp == -1 | cip == -1:
                return
            else:
                disable_inputs()
                wan_scan(i, st, en)

        def set_start_port_box(text):
            start_port_box.delete(0, END)
            start_port_box.insert(0, text)
            return

        def set_end_port_box(text):
            end_port_box.delete(0, END)
            end_port_box.insert(0, text)
            return

        def enable_status_box():
            status_box['state'] = 'normal'

        def disable_status_box():
            status_box['state'] = 'disabled'

        def set_status_box(text):
            enable_status_box()
            status_box.delete(0, END)
            status_box.insert(0, text)
            disable_status_box()
            return

        def wan_scan(remote_ip, start, end):
            disable_inputs()
            set_status_box(running)

            t1 = datetime.now()

            res = progress_math(start, end)

            open_ports = 0
            try:
                for port_scan in range(int(start), int(end)):
                    cp_res = connected_ports(remote_ip, port_scan)
                    bar['value'] += res
                    bar.update()

                    if cp_res == 0:
                        query = querysql(port_scan)
                        if query == -1:
                            set_status_box(failure)
                            return
                        elif query == 0:
                            query = 'None'

                        open_ports += 1
                        for r in query:
                            insert_into_tree(port_scan, r[0], r[2], r[3])
                            time.sleep(1)
                bar['value'] += res

            except socket.gaierror:
                print('Hostname could not be resolved. Exiting')
                set_status_box(failure)
                return

            except socket.error:
                print("Couldn't connect to server")
                set_status_box(failure)
                return

            t2 = datetime.now()

            total = t2 - t1
            print(total)
            enable_inputs()
            set_status_box(completed)

        def progress_math(start_port, end_port):
            frac = int(end_port) - int(start_port) + 1
            res = 100 / frac
            return res

        def set_ip_box(ip):
            ip_box.delete(0, END)
            ip_box.insert(0, ip)
            return

        def get_external_ip():
            ip = get_remote_server_ip()
            set_ip_box(ip)
            set_start_port_box(1)
            set_end_port_box(65535)

        return_home = tk.Button(self, text="Back to Home", pady='8', command=lambda: controller.show_frame(StartPage))
        return_home.pack()

        get_my_external_ip = tk.Button(self, text="Get My External IP", pady='8', command=get_external_ip)

        ip_box = Entry(self, width=16)
        start_port_box = Entry(self, width=5)
        end_port_box = Entry(self, width=5)
        ip_label = Label(self, text='IP:')
        start_port_label = Label(self, text='Starting Port:')
        end_port_label = Label(self, text='Ending Port:')

        ip_label.place(x=220, y=101)
        ip_box.place(x=250, y=100)
        get_my_external_ip.place(x=260, y=140)

        start_port_label.place(x=240, y=191)
        start_port_box.place(x=340, y=190)
        end_port_label.place(x=240, y=231)
        end_port_box.place(x=340, y=230)

        status_box = Entry(self, width=15, state='disabled')
        status_label = Label(self, text='Status:')
        status_box.place(x=490, y=80)
        status_label.place(x=490, y=50)

        set_status_box(ready)

        start_scan = tk.Button(self, text="Start Scan", pady='8', command=start)
        start_scan.place(x=280, y=280)

        port_results = ttk.Treeview(self)
        port_results.pack(fill=X, padx='10', side='bottom')
        port_results['columns'] = ('status', 'service', 'protocol', 'vulnerability')
        port_results.heading('#0', text='Port', anchor='w')
        port_results.column('#0', anchor='center', width=13)
        port_results.heading('status', text='Status')
        port_results.column('status', anchor='center', width=20)
        port_results.heading('service', text='Service')
        port_results.column('service', anchor='center', width=100)
        port_results.heading('protocol', text='Protocol')
        port_results.column('protocol', anchor='center', width=10)
        port_results.heading('vulnerability', text='Vulnerability')
        port_results.column('vulnerability', anchor='center', width=100)
        bar.pack(side='bottom', after=port_results, pady='5')


app = MainApplication()
app.wm_geometry("650x550")
app.title("PortGuard")
windowWidth = app.winfo_reqwidth()
windowHeight = app.winfo_reqheight()
positionRight = int(app.winfo_screenwidth() / 3 - windowWidth / 3)
positionDown = int(app.winfo_screenheight() / 3 - windowHeight / 3)
app.geometry("+{}+{}".format(positionRight, positionDown))
app.configure(background='#3a3e44')
app.resizable(False, False)

if __name__ == '__main__':
    app.mainloop()
