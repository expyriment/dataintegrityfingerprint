#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals



try:
    import tkinter as tk
    from tkinter.filedialog import askdirectory, asksaveasfilename
except:
    # proably python 2
    import Tkinter as tk
    from tkFileDialog import askdirectory, asksaveasfile

from . import DataIntegrityFingerprint as DIF


class TK_GUI(tk.Tk):
    def __init__(self, root):

        self.directory = None
        self.dif = None
        self._hashlist_calculated = False

        # GUI
        tk.Tk.__init__(self, root)
        self.root = root
        self.resizable(width=False,height=False)
        self.protocol('WM_DELETE_WINDOW', self.close)

        self.title('Data Integrity Fingerprint GUI')

        # menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Select Folder", command=self.select_folder)
        filemenu.add_separator()
        filemenu.add_command(label="Make Hashes",
                             command=self.make_hashes, state=tk.DISABLED)
        filemenu.add_command(label="Save Hash List", command=self.save,
                        state=tk.DISABLED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="Data", menu=filemenu)

        self.hash_menu = tk.Menu(menubar, tearoff=0)

        aboutmenu = tk.Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About...", command=self.about)
        menubar.add_cascade(label="About", menu=aboutmenu)
        self.config(menu=menubar)
        self.filemenu = filemenu

        # Frame 1
        frame1 = tk.Frame(self)
        frame1.pack(side = tk.TOP)

        ##  folder label
        frame_folder = tk.Frame(frame1)
        frame_folder.pack(side=tk.TOP)
        tk.Label(frame_folder, text="Folder:", width=7,
                            anchor=tk.W).pack(side=tk.LEFT)
        self.foldername = tk.StringVar()
        label_folder = tk.Label(frame_folder,
                textvariable=self.foldername, anchor=tk.W, width=80)
        label_folder.pack(side=tk.RIGHT)

        ## master hash frame (bottom)
        frame_master = tk.Frame(frame1)
        frame_master.pack(side = tk.BOTTOM)
        tk.Label(frame_master, text="Master hash:", width=11,
                            anchor=tk.W).pack(side=tk.LEFT)
        self.master_hash_text = tk.Text(frame_master, height=1,
                            borderwidth=0, width=85, relief=tk.SUNKEN)
        self.master_hash_text.pack(side=tk.RIGHT)

        ## text with Scrollbar
        xscrollbar = tk.Scrollbar(frame1, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        yscrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output = tk.Text(frame1, height=20, width=80,
                                   borderwidth=3, relief="sunken",
                                   yscrollcommand=yscrollbar.set,
                                   xscrollcommand=xscrollbar.set)
        self.text_output.config(font=("courier", 10), undo=True, wrap=tk.NONE)
        self.text_output.pack( side = tk.TOP, fill = tk.BOTH )
        xscrollbar.config( command = self.text_output.xview)
        yscrollbar.config( command = self.text_output.yview)

        # Frame2: Button frame
        frame_btn = tk.Frame(self)
        frame_btn.pack(side = tk.BOTTOM, fill = tk.X)

        self.algorithm = tk.StringVar()
        self.algorithm.set("sha256") # initialize
        tk.Label(frame_btn, text="Hash algorithm:", width=13,
                            anchor=tk.W).pack(side=tk.LEFT)
        alg_menu = tk.OptionMenu(frame_btn, self.algorithm,
                                 *DIF.available_algorithms,
                command=self.change_algorithm)
        alg_menu.pack(side = tk.LEFT, anchor=tk.W)

        bbutton= tk.Button(frame_btn, text="Select Folder",
                            command=self.select_folder, height=2, width=10)
        bbutton.pack(side = tk.RIGHT, fill=tk.X)

        self.recalc_btn = tk.Button(frame_btn, text="Make Hashes",
                                        command=self.make_hashes, height=2,
                                    width=10, state = tk.DISABLED)
        self.recalc_btn.pack(side = tk.RIGHT, fill=tk.X)


    def select_folder(self):
        tk.Tk().withdraw()
        d = askdirectory()
        if len(d)>1:
            self.directory = d
            self.foldername.set(d)
            self.title("DIF GUI: " + str(d))
            self.update()

            self.make_hashes()


    def make_hashes(self):
        if self.directory is not None:
            self.master_hash_text.delete(1.0, tk.END)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.INSERT, "Please wait....")
            self.update()

            self.dif = DIF(data = self.directory,
                           hash_algorithm=self.algorithm.get())

            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.INSERT, self.dif.checksums)
            self.master_hash_text.insert(tk.INSERT,
                                        "{0}".format(self.dif.master_hash))
            self._hashlist_calculated = True
            self.filemenu.entryconfigure(3, state=tk.ACTIVE)  # save
            self.recalc_btn.config(state=tk.DISABLED) # re-calc
            self.filemenu.entryconfigure(2, state=tk.DISABLED) # re-calc

    def change_algorithm(self, new_alogo):
        if self._hashlist_calculated:
            self.recalc_btn.config(state= tk.ACTIVE)
            self.filemenu.entryconfigure(2, state = tk.ACTIVE)

    def close(self):
        quit()

    def about(self):
        #todo
        pass

    def save(self):
        if self.dif is None:
            return
        filetypes = list(map(lambda x: (x, "."+x),
                            DIF.algorithms_guaranteed))
        filetypes.append(("All Files", "*.*"))
        default = (self.algorithm.get(), "."+self.algorithm.get())
        filetypes.remove(default)
        filetypes.insert(0, default)
        flname = asksaveasfilename(defaultextension=default[1],
                                filetypes=filetypes)
        if len(flname)>0:
            self.dif.save_checksums(flname)

if __name__ == "__main__":
    app = TK_GUI(None)
    app.mainloop()
