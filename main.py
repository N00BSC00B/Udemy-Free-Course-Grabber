import requests
from bs4 import BeautifulSoup
import tkinter
import webbrowser
from PIL import Image, ImageTk
import os
import sys
import threading

mainWindow = tkinter.Tk()


def resource_path(relative_path: str):
    """
    Function to find the Path of the given file in Relative Path.

    :param relative_path: The Relative Path of the file.
    :return: str: The Actual Path of the file.
    """

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


a = Image.open(resource_path("assets/logo.png"))
logo = ImageTk.PhotoImage(a)

get = requests.get(
    "https://answersq.com/udemy-paid-courses-for-free-with-certificate/"
)
soup = BeautifulSoup(get.content, "html.parser")
ul_ele = soup.find_all("ul", class_="has-medium-font-size")

active = []
activeD = {}
height = 400
width = 400
bg = "#36393E"


def open_url(event):
    lab = event.widget
    course = lab.cget("text")

    url = activeD[course]

    webbrowser.open_new_tab(url)


def enter(event):
    lab = event.widget
    lab.config(fg="#87CEFA")


def leave(event):
    lab = event.widget
    lab.config(fg="white")


def on_mousewheel(event):
    steps = -1 * (int(event.delta) / 120)
    canva.yview_scroll(int(steps), "units")


def search(e=None):
    global active
    for i in active:
        i.destroy()

    active = []

    user = entry.get()
    send = []

    r = 0

    for ul in ul_ele:
        for li_ele in ul.find_all("li"):
            for i in li_ele.find_all("a"):
                got = str(i.text)

                if user.lower() in got.lower():
                    if got not in send:
                        url = i.get("href")
                        send.append(got)

                        Clabel = tkinter.Label(
                            f2,
                            text=got,
                            font=("Garamond 12 underline"),
                            bg=bg,
                            fg="white",
                            anchor="nw",
                            wraplength=width - 55,
                            cursor="hand2",
                        )

                        arrow = tkinter.Label(
                            f2,
                            text="»",
                            font=("Garamond 12"),
                            bg=bg,
                            fg="white",
                            anchor="nw",
                        )

                        Clabel.grid(row=r, column=1, sticky="nw")
                        arrow.grid(row=r, column=0, sticky="nw")
                        Clabel.bind("<Button-1>", open_url)
                        active.append(Clabel)
                        active.append(arrow)
                        activeD[got] = url

                        r += 1

    if active == []:
        Clabel = tkinter.Label(
            f2,
            text=f"No Course on {user} found today, "
                 "check back again tomorrow.",
            font=("Garamond 15"),
            bg=bg,
            fg="white",
            anchor="center",
            wraplength=width - 55,
            cursor="hand2",
        )

        Clabel.grid(row=r, column=1, sticky="ew")

        active.append(Clabel)


mainWindow.title("Udemy Free Courses")
mainWindow.geometry(f"{width}x{height}")
mainWindow.resizable(False, False)
mainWindow.configure(bg=bg)
mainWindow.iconphoto(False, logo)

f1 = tkinter.Frame(
    mainWindow,
    height=60,
    width=width,
    bd=10,
    bg=bg,
    relief="sunken"
)
f1.grid(row=0, column=0, columnspan=2)

part = tkinter.LabelFrame(mainWindow, bg=bg)
canva = tkinter.Canvas(part, width=width - 30, height=300, bg=bg)
f2 = tkinter.Frame(canva, height=10, width=width - 50, bg=bg)
f2.grid_propagate(1)

canva.create_window((2, 2), window=f2, anchor="nw")
canva.pack(side=tkinter.LEFT, fill="both", expand="yes")
part.grid(row=1, column=0)

yscrollbar = tkinter.Scrollbar(part, orient="vertical", command=canva.yview)
yscrollbar.pack(side=tkinter.RIGHT, fill="y", padx=5)
canva.configure(yscrollcommand=yscrollbar.set)

l1 = tkinter.Label(
    f1,
    text="Enter keyword to search: ",
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 11"),
)
entry = tkinter.Entry(f1, width=27)
b1 = tkinter.Button(
    f1,
    text="Search",
    command=lambda: threading.Thread(target=search).start(),
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 11"),
)

l2 = tkinter.Label(
    f1,
    text="NOTE: The offers are for limited time and for limited users. "
         "Some offers might end by the time you visit the coursee.",
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 10"),
    wraplength=width - 50,
)

# Frame 1
l1.grid(row=0, column=0)
entry.grid(row=0, column=1)
b1.grid(row=0, column=2, padx=5)
l2.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

# Binds
canva.bind(
    "<Configure>",
    lambda e: canva.configure(scrollregion=canva.bbox("all"))
)
f2.bind(
    "<Configure>",
    lambda e: canva.configure(scrollregion=canva.bbox("all"))
)
canva.bind_all("<MouseWheel>", on_mousewheel)
entry.bind("<Return>", search)

mainWindow.mainloop()
