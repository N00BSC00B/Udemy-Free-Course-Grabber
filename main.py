# Import necessary libraries
import tkinter as tk
import webbrowser
from PIL import Image, ImageTk
import os
import sys
import threading
import scrap

# Create the main window
mainWindow = tk.Tk()


# Define a function to find the path of a given file in relative path
def resource_path(relative_path: str) -> str:
    """
    Function to find the Path of the given file in Relative Path.

    :param relative_path: The Relative Path of the file.
    :return: str: The Actual Path of the file.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Open the image file and create a PhotoImage object
logo = ImageTk.PhotoImage(Image.open(resource_path("assets/logo.png")))

# Initialize variables
active = []
activeD = {}
height = 400
width = 400
bg = "#36393E"


# Define a function to open the URL of a course when its label is clicked
def open_url(event: tk.Event) -> None:
    """
    Function to open the URL of a course when its label is clicked.

    :param event: The event object.
    :return: None.
    """
    course = event.widget.cget("text")
    url = activeD[course]
    webbrowser.open_new_tab(url)


# Define a function to change the color of a label when the mouse enters it
def enter(event: tk.Event) -> None:
    """
    Function to change the color of a label when the mouse enters it.

    :param event: The event object.
    :return: None.
    """
    event.widget.config(fg="#87CEFA")


# Define a function to change the color of a label when the mouse leaves it
def leave(event: tk.Event) -> None:
    """
    Function to change the color of a label when the mouse leaves it.

    :param event: The event object.
    :return: None.
    """
    event.widget.config(fg="white")


# Define a function to scroll the canvas when the mouse wheel is used
def on_mousewheel(event: tk.Event) -> None:
    """
    Function to scroll the canvas when the mouse wheel is used.

    :param event: The event object.
    :return: None.
    """
    steps = -1 * (int(event.delta) / 120)
    canva.yview_scroll(int(steps), "units")


# Define a function to search for courses based on a keyword
def search(e: tk.Event = None) -> None:
    """
    Function to search for courses based on a keyword.

    :param e: The event object.
    :return: None.
    """
    global active
    for widget in active:
        widget.destroy()
    active = []
    user = entry.get()
    r = 0
    data = scrap.get_course(user)
    got = None  # Initialize got variable
    for got, url in data.items():
        Clabel = tk.Label(
            f2,
            text=got,
            font=("Garamond 12 underline"),
            bg=bg,
            fg="white",
            anchor="nw",
            wraplength=width - 55,
            cursor="hand2",
        )
        arrow = tk.Label(
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
        Clabel.bind("<Enter>", enter)
        Clabel.bind("<Leave>", leave)
        active.append(Clabel)
        active.append(arrow)
        activeD[got] = url
        r += 1
    if not got:
        Clabel = tk.Label(
            f2,
            text=(
                f"No Course on {user} found today, "
                "check back again tomorrow."
            ),
            font=("Garamond 15"),
            bg=bg,
            fg="white",
            anchor="center",
            wraplength=width - 55,
            cursor="hand2",
        )
        Clabel.grid(row=r, column=1, sticky="ew")
        active.append(Clabel)


# Set up the main window
mainWindow.title("Udemy Free Courses")
mainWindow.geometry(f"{width}x{height}")
mainWindow.resizable(False, False)
mainWindow.configure(bg=bg)
mainWindow.iconphoto(False, logo)

# Create the frames and widgets
f1 = tk.Frame(
    mainWindow, height=60, width=width, bd=10, bg=bg, relief="sunken"
)
f1.grid(row=0, column=0, columnspan=2)

part = tk.LabelFrame(mainWindow, bg=bg)
canva = tk.Canvas(part, width=width - 30, height=300, bg=bg)
f2 = tk.Frame(canva, height=10, width=width - 50, bg=bg)
f2.grid_propagate(1)

canva.create_window((2, 2), window=f2, anchor="nw")
canva.pack(side=tk.LEFT, fill="both", expand="yes")
part.grid(row=1, column=0)

yscrollbar = tk.Scrollbar(part, orient="vertical", command=canva.yview)
yscrollbar.pack(side=tk.RIGHT, fill="y", padx=5)
canva.configure(yscrollcommand=yscrollbar.set)

l1 = tk.Label(
    f1,
    text="Enter keyword to search: ",
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 11"),
)
entry = tk.Entry(f1, width=27)
b1 = tk.Button(
    f1,
    text="Search",
    command=lambda: threading.Thread(target=search).start(),
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 11"),
)

l2 = tk.Label(
    f1,
    text=("NOTE: The offers are for limited time and for limited users. "
          "Some offers might end by the time you visit the course."),
    anchor="n",
    bg=bg,
    fg="white",
    font=("Garamond 10"),
    wraplength=width - 50,
)

# Add the widgets to the frames
l1.grid(row=0, column=0)
entry.grid(row=0, column=1)
b1.grid(row=0, column=2, padx=5)
l2.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

# Bind the events to the widgets
canva.bind("<Configure>", lambda e: canva.configure(
    scrollregion=canva.bbox("all")
))
f2.bind("<Configure>", lambda e: canva.configure(
    scrollregion=canva.bbox("all")
))
canva.bind_all("<MouseWheel>", on_mousewheel)
entry.bind("<Return>", search)

# Start the main loop
mainWindow.mainloop()
