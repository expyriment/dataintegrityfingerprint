#!/usr/bin/env python3

"""Data Integrity Fingerprint GUI.

A GUI for the Data Integrity Fingerprint (DIF) Python reference implementation.

"""

__author__ = 'Oliver Lindemann <oliver@expyriment.org>, ' +\
             'Florian Krause <florian@expyriment.org>'


import os
import sys
import platform
import multiprocessing
from threading import Thread
from .hashing import CRYPTOGRAPHIC_ALGORITHMS

if sys.version[0] == '3':
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import filedialog, messagebox
    from tkinter.scrolledtext import ScrolledText
else:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    from ScrolledText import ScrolledText

from . import DataIntegrityFingerprint as DIF


class App(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.master.title("Data Integrity Fingerprint (DIF)")
        self.about_text = """Data Integrity Fingerprint (DIF)

Reference Python implementation

Authors:
Oliver Lindemann <oliver@expyriment.org>
Florian Krause <florian@expyriment.org>
"""
        self.dif = None
        self.create_widgets()
        self.dir_button.focus()

    def create_widgets(self):
        """Create GUI widgets."""

        # Menu
        self.menubar = tk.Menu(self.master)
        if platform.system() == "Darwin":
            modifier = "Command"
            self.apple_menu = tk.Menu(self.menubar, name="apple")
            self.menubar.add_cascade(menu=self.apple_menu)
            self.apple_menu.add_command(
                label="About Data Integrity Fingerprint (DIF)",
                command=lambda: messagebox.showinfo("About", self.about_text))
        else:
            modifier = "Control"
        self.file_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.file_menu.add_command(label="Open checksums",
                                   command=self.open_checksums,
                                   accelerator="{0}-O".format(modifier))
        self.master.bind("<{0}-o>".format(modifier), self.open_checksums)
        self.file_menu.add_command(label="Save checksums",
                                   command=self.save_checksums,
                                   accelerator="{0}-S".format(modifier))
        self.master.bind("<{0}-s>".format(modifier), self.save_checksums)
        self.file_menu.add_command(label="Quit",
                                   command=self.master.destroy,
                                   accelerator="{0}-Q".format(modifier))
        self.master.bind("<{0}-q>".format(modifier),
                         lambda event: self.master.destroy())
        self.file_menu.entryconfig("Save checksums", state=tk.DISABLED)
        self.options_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.options_menu, label="Options")
        self.algorithm_menu = tk.Menu(self.menubar)
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("sha256")
        for algorithm in CRYPTOGRAPHIC_ALGORITHMS:
            self.algorithm_menu.add_radiobutton(label=algorithm,
                                                value=algorithm,
                                                variable=self.algorithm_var)
        self.options_menu.add_cascade(menu=self.algorithm_menu,
                                      label="Hash algorithm")
        self.update_menu = tk.Menu(self.menubar)
        self.update_var = tk.IntVar()
        self.update_var.set(1)
        self.update_menu.add_radiobutton(label="on", value=1,
                                         variable=self.update_var)
        self.update_menu.add_radiobutton(label="off (faster)", value=0,
                                         variable=self.update_var)
        self.options_menu.add_cascade(menu=self.update_menu,
                                      label="Progress updating")
        self.multiprocess_var = tk.IntVar()
        self.multiprocess_var.set(0)
        if multiprocessing.cpu_count() > 1:
            self.multiprocess_var.set(1)
            self.multiprocess_menu = tk.Menu(self.menubar)
            self.multiprocess_menu.add_radiobutton(
                label="on ({0} cores)".format(
                    multiprocessing.cpu_count()),
                value=1,
                variable=self.multiprocess_var)
            self.multiprocess_menu.add_radiobutton(
                label="off", value=0, variable=self.multiprocess_var)
            self.options_menu.add_cascade(menu=self.multiprocess_menu,
                                          label="Multi-core processing")
        self.help_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")
        self.help_menu.add_command(
            label="About",
            command=lambda: messagebox.showinfo("About", self.about_text))

        self.master["menu"] = self.menubar

        # Main window
        self.frame1 = ttk.Frame(self.master)
        self.frame1.grid(row=0, column=0, sticky="NSWE") #, padx=5, pady=5)
        self.frame1.grid_columnconfigure(1, weight=1)
        self.dir_label = ttk.Label(self.frame1, text="Data directory:")
        self.dir_label.grid(row=0, column=0)
        self.dir_var = tk.StringVar()
        self.dir_var.set("")
        self.dir_entry = ttk.Entry(self.frame1, textvariable=self.dir_var,
                                   takefocus=0, state=tk.DISABLED)
        self.dir_entry.grid(row=0, column=1, sticky="WE") #, padx=5)
        self.dir_button = ttk.Button(self.frame1, text="Browse",
                                     command=self.set_data_directory)
        self.dir_button.grid(row=0, column=2)
        self.generate_button = ttk.Button(
            self.frame1, text="Generate DIF",
            command=lambda: Thread(target=self.generate_dif,
                                   daemon=True).start(),
            state=tk.DISABLED)
        self.generate_button.grid(row=0, column=3)

        self.progressbar = ttk.Progressbar(self.master)
        self.progressbar.grid(row=1, column=0, sticky="NSWE")

        self.container = ttk.Frame(self.master, borderwidth=1,
                                   relief=tk.SUNKEN)
        self.checksum_list = tk.Text(self.container, wrap="none",
                                     borderwidth=0, state=tk.DISABLED)
        self.vertical_scroll = ttk.Scrollbar(self.container, orient="vertical",
                                             command=self.checksum_list.yview)
        self.horizontal_scroll = ttk.Scrollbar(
            self.container, orient="horizontal",
            command=self.checksum_list.xview)
        self.checksum_list.configure(yscrollcommand=self.vertical_scroll.set,
                                     xscrollcommand=self.horizontal_scroll.set)
        self.checksum_list.grid(row=0, column=0, sticky="NSWE")
        self.vertical_scroll.grid(row=0, column=1, sticky="NS")
        self.horizontal_scroll.grid(row=1, column=0, sticky="EW")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid(row=2, column=0, sticky="NSWE")

        self.frame2 = ttk.Frame(self.master)
        self.frame2.grid(row=3, column=0, sticky="NSWE")
        self.frame2.grid_columnconfigure(1, weight=1)
        self.dif_label = ttk.Label(self.frame2, text="DIF ({0}):".format(
            self.algorithm_var.get()))
        self.dif_label.grid(row=0, column=0)
        self.dif_var = tk.StringVar()
        self.dif_var.set("")
        self.dif_entry = ttk.Entry(self.frame2, textvariable=self.dif_var,
                                   takefocus=0, foreground="black",
                                   state=tk.DISABLED)
        self.dif_entry.grid(row=0, column=1, sticky="NSWE")
        self.copy_button = ttk.Button(self.frame2, text="Copy",
                                      command=self.copy_dif_to_clipboard,
                                      state=tk.DISABLED)
        self.copy_button.grid(row=0, column=2)

        # Status bar
        self.statusbar = ttk.Label(self.master, text="", border=1,
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.grid(row=4, column=0, sticky="WE")

    def set_data_directory(self, *args):
        "Set the data directory."""

        data_dir = filedialog.askdirectory()
        if data_dir != "":
            self.dir_var.set(data_dir + "/")
            self.generate_button["state"] = tk.NORMAL
            self.generate_button.focus()
            self.progressbar["value"] = 0
            self.checksum_list["state"] = tk.NORMAL
            self.checksum_list.delete(1.0, tk.END)
            self.checksum_list["state"] = tk.DISABLED
            self.dif_var.set("")
            self.dif = None
            self.statusbar["text"] = "Ready"

    def block_gui(self):
        """Block GUI from user entry."""

        self.file_menu.entryconfig("Open checksums", state=tk.DISABLED)
        self.file_menu.entryconfig("Save checksums", state=tk.DISABLED)
        self.options_menu.entryconfig("Hash algorithm", state=tk.DISABLED)
        self.options_menu.entryconfig("Progress updating", state=tk.DISABLED)
        self.options_menu.entryconfig("Multi-core processing",
                                      state=tk.DISABLED)
        self.help_menu.entryconfig("About", state=tk.DISABLED)
        self.progressbar.grab_set()

    def unblock_gui(self):
        """Unblock GUI from user entry."""

        self.file_menu.entryconfig("Open checksums", state=tk.NORMAL)
        self.file_menu.entryconfig("Save checksums", state=tk.NORMAL)
        self.options_menu.entryconfig("Hash algorithm", state=tk.NORMAL)
        self.options_menu.entryconfig("Progress updating", state=tk.NORMAL)
        self.options_menu.entryconfig("Multi-core processing",
                                      state=tk.NORMAL)
        self.help_menu.entryconfig("About", state=tk.NORMAL)
        self.progressbar.grab_release()

    def generate_dif(self, *args):
        """Generate DIF from data directory"""

        def _progress(count, total, status=''):
            """Progress callback function"""

            percents = int(round(100.0 * count / float(total), 1))
            self.progressbar["value"] = percents
            self.statusbar["text"] = \
                "Generating DIF...{0}% ({1})".format(percents, status)

        self.block_gui()
        self.statusbar["text"] = "Generating DIF..."
        if self.multiprocess_var.get() == 1:
            multiprocessing = True
        else:
            multiprocessing = False
        self.dif = DIF(self.dir_entry.get(),
                       hash_algorithm=self.algorithm_var.get(),
                       multiprocessing=multiprocessing)
        if self.update_var.get() == 1:
            progress=_progress
        else:
            progress=None
        self.dif.generate(progress=progress)
        self.progressbar["value"] = 100
        self.checksum_list["state"] = tk.NORMAL
        self.checksum_list.delete(1.0, tk.END)
        self.checksum_list.insert(1.0, self.dif.checksums.strip("\n"))
        self.checksum_list["state"] = tk.DISABLED
        self.dif_label.config(text="DIF ({0}):".format(
            self.algorithm_var.get()))
        self.dif_var.set(self.dif.master_hash)
        self.copy_button["state"] = tk.NORMAL
        self.copy_button.focus()
        self.statusbar["text"] = "Generating DIF...Done"
        self.unblock_gui()

    def open_checksums(self, *args):
        """Open checksums file."""

        filename = filedialog.askopenfilename()
        self.block_gui()
        try:
            self.statusbar["text"] = "Opening checksums file '{0}'...".format(
                filename)

            algorithm = os.path.splitext(filename)[-1].strip(".")
            self.dif = DIF(filename, from_checksums_file=True,
                           hash_algorithm=self.algorithm_var.get())
            self.dir_var.set("")
            self.generate_button["state"] = tk.DISABLED
            self.progressbar["value"] = 100
            self.checksum_list["state"] = tk.NORMAL
            self.checksum_list.delete(1.0, tk.END)
            self.checksum_list.insert(1.0, self.dif.checksums.strip("\n"))
            self.checksum_list["state"] = tk.DISABLED
            self.dif_label.config(text="DIF ({0}):".format(
                algorithm))
            self.dif_var.set(self.dif.master_hash)
            self.copy_button["state"] = tk.NORMAL
            self.copy_button.focus()
            self.statusbar["text"] = \
                "Opening checksums file '{0}'...Done".format(filename)
        except:
            pass
        self.unblock_gui()

    def save_checksums(self, *args):
        "Save checksums file."""

        if self.checksum_list.get(1.0, tk.END).strip("\n") != "":
            self.dif.save_checksums(filename=filedialog.asksaveasfilename(
                defaultextension=self.algorithm_var.get(),
                initialdir=os.path.split(self.dir_entry.get())[0],
                initialfile=os.path.split(self.dir_entry.get())[-1]))

    def copy_dif_to_clipboard(self, *args):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.dif_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    #if platform.system() == "Linux":
        #style = Style()
        #style.theme_use("clam")
    root.bind_class("TButton", "<Return>",
                    lambda event: event.widget.invoke())
    root.option_add('*tearOff', tk.FALSE)
    root.geometry("1024x600")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(2, weight=1)
    app = App(root)
    app.mainloop()
