import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import tkinter.ttk as ttk

LARGE_FONT = ("Verdana", 25)
background_color = '#3a3e44'


def scan():
    print('scan')


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

        return_home = tk.Button(self, text="Back to Home", pady='5', command=lambda: controller.show_frame(StartPage))
        return_home.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Scan My External IP", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        return_home = tk.Button(self, text="Back to Home", pady='8', command=lambda: controller.show_frame(StartPage))
        return_home.pack()

        get_my_external_ip = tk.Button(self, text="Get My External IP", pady='8')

        ip_box = Entry(self, width=16)
        start_port_box = Entry(self, width=5)
        end_port_box = Entry(self, width=5)
        ip_label = Label(self, text='IP:')
        start_port_label = Label(self, text='Starting Port:')
        end_port_label = Label(self, text='Ending Port:')
        #
        ip_label.place(x=220, y=101)
        ip_box.place(x=250, y=100)

        get_my_external_ip.place(x=260, y=140)

        start_port_label.place(x=240, y=191)
        start_port_box.place(x=340, y=190)
        end_port_label.place(x=240, y=231)
        end_port_box.place(x=340, y=230)

        start_scan = tk.Button(self, text="Start Scan", pady='8', command=scan)
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
