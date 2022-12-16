import tkinter as tk

class GUI:      # we do everything inside a class to make it easier for GUI elements and functions to interact

    def __init__(self) -> None:         # initiator contains the main GUI code
        self.root = tk.Tk()                                     # instantiate the Tk class. root is the standard name for this object

        self.root.geometry("1000x800")                          # define default window size and title
        self.root.title("The Dogshit Digital Amplifier")

        self.root.mainloop()                                    # render the root Tk window

GUI()       # instantiating GUI object constructs Tk window via __init__