#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

from data_fingerprint import HashData, PY3, string_encode

import tkinter as tk
from tkinter import messagebox

if PY3:
    from tkinter.filedialog import askdirectory, asksaveasfile
else:
    from tkFileDialog import askdirectory, asksaveasfile



class DataFingerprintGUI(tk.Tk):
    def __init__(self, root):

        self.dirctory = None

        # GUI
        tk.Tk.__init__(self, root)
        self.root = root
        self.resizable(width=False,height=False)
        self.protocol('WM_DELETE_WINDOW', self.close)

        # menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Select Folder", command=self.select_folder)
        filemenu.add_separator()
        filemenu.add_command(label="Recalculate Hashes", command=self.make_hashes, state=tk.DISABLED)
        filemenu.add_command(label="Save Hash List", command=self.save, state=tk.DISABLED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="Data", menu=filemenu)

        aboutmenu = tk.Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About...", command=self.about)
        menubar.add_cascade(label="About", menu=aboutmenu)
        self.config(menu=menubar)
        self.filemenu = filemenu


        # Frame 1
        frame1 = tk.Frame(self)
        frame1.pack(side = tk.TOP)

        ##  folder lable
        frame_folder = tk.Frame(frame1)
        frame_folder.pack(side=tk.TOP)
        tk.Label(frame_folder, text="Folder:", width=6, anchor=tk.W).pack(side=tk.LEFT)
        self.foldername = tk.StringVar()
        label_folder = tk.Label(frame_folder, textvariable=self.foldername, anchor=tk.W, width=80)
        label_folder.pack(side=tk.LEFT)

        ## master hash frame (bottom)
        frame_master = tk.Frame(frame1)
        frame_master.pack(side = tk.BOTTOM)
        tk.Label(frame_master, text="Master hash:", width=11, anchor=tk.W).pack(side=tk.LEFT)
        self.master_hash_text = tk.Text(frame_master, height=1, borderwidth=0, width=85, relief=tk.SUNKEN)
        self.master_hash_text.pack(side=tk.RIGHT)

        ## text with Scrollbar
        xscrollbar = tk.Scrollbar(frame1, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        yscrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output = tk.Text(frame1, height=20, width=80, borderwidth=3, relief="sunken",
                                   yscrollcommand= yscrollbar.set,
                                   xscrollcommand= xscrollbar.set)
        self.text_output.config(font=("courier", 10), undo=True, wrap=tk.NONE)
        self.text_output.pack( side = tk.TOP, fill = tk.BOTH )
        xscrollbar.config( command = self.text_output.xview)
        yscrollbar.config( command = self.text_output.yview)

        # Frame2: Button frame
        frame_btn = tk.Frame(self)
        frame_btn.pack(side = tk.BOTTOM, fill = tk.X)

        self.algorithm = tk.StringVar()
        self.algorithm.set("sha1") # initialize
        self.supported_algorithm = ["sha1", "md5", "sha256"]
        for mode in self.supported_algorithm:
            b = tk.Radiobutton(frame_btn, text=mode, variable=self.algorithm,
                               value=mode, command=self.change_algorithm)
            b.pack(side = tk.LEFT, anchor=tk.W)


        bbutton= tk.Button(frame_btn, text="Select folder", command=self.select_folder, height=2, width=10)
        bbutton.pack(side = tk.RIGHT, fill=tk.X)

        self._hashlist_calculated = False
        self.recalc_btn = tk.Button(frame_btn, text="Make hashes", command=self.make_hashes, height=2,
                                    width=10, state = tk.DISABLED)
        self.recalc_btn.pack(side = tk.RIGHT, fill=tk.X)


    def select_folder(self):
        tk.Tk().withdraw()
        self.dirctory = askdirectory()
        self.foldername.set(self.dirctory)
        self.update()

        self.title("Data Fingerprint: "+ str(self.dirctory))
        self.make_hashes()


    def make_hashes(self):
        if self.dirctory is not None:
            self.master_hash_text.delete(1.0, tk.END)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.INSERT, "Please wait....")
            self.update()

            data_hash = HashData(path = self.dirctory, algorithm=self.algorithm.get(),
                                 multiprocessing=False)

            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.INSERT, data_hash.to_string())
            self.master_hash_text.insert(tk.INSERT,
                            "{0} (short: {1})".format(data_hash.master_hash, \
                                                      data_hash.master_hash_short))
            self._hashlist_calculated = True
            self.filemenu.entryconfigure(3, state=tk.ACTIVE)  # save
            self.recalc_btn.config(state=tk.DISABLED) # re-calc
            self.filemenu.entryconfigure(2, state=tk.DISABLED) # re-calc

    def change_algorithm(self):
        if self._hashlist_calculated:
            self.recalc_btn.config(state= tk.ACTIVE)
            self.filemenu.entryconfigure(2, state = tk.ACTIVE)

    def close(self):
        quit()

    def about(self):
        #todo
        pass

    def save(self):

        filetypes = list(map(lambda x: (x, "."+x), self.supported_algorithm))
        filetypes.append(("All Files", "*.*"))

        file = asksaveasfile(mode='w', defaultextension=".{0}".format(self.algorithm.get()),
                             filetypes=filetypes)
        txt = self.text_output.get(1.0, tk.END)[:-1]
        if PY3:
            file.write(txt)
        else:
            file.write(string_encode(txt))
        file.close()

def start_gui():
    app = DataFingerprintGUI(None)
    app.title('Data Fingerprint')
    app.mainloop()

if __name__ == "__main__":
    start_gui()