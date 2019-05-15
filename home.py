import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image

LARGE_FONT = ("Verdana", 25)
background_color = '#3a3e44'


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

        button1 = tk.Button(self, text="Back to Home", pady='10',
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Scan My External IP", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Back to Home", pady='10',
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()


app = MainApplication()
app.wm_geometry("650x550")
app.title("PortGuard")
windowWidth = app.winfo_reqwidth()
windowHeight = app.winfo_reqheight()
positionRight = int(app.winfo_screenwidth() / 3 - windowWidth / 3)
positionDown = int(app.winfo_screenheight() / 3 - windowHeight / 3)
print("Width", windowWidth, "Height", windowHeight)
app.geometry("+{}+{}".format(positionRight, positionDown))
app.configure(background='#3a3e44')
app.resizable(False, False)

if __name__ == '__main__':
    app.mainloop()
