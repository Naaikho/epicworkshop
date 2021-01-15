from lxml import html
import requests
import sys, os
import json
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning
import traceback
import threading
import wget

def getDownloadLink(miss_map:list):
    """ get all maps download links in a json file on mediafire """
    r = requests.get("https://download1513.mediafire.com/...") # normally, the link redirects to a json file which contains a list of links to download RL maps
    rq = []
    res = []

    for link in r.json().items():
        for missM in miss_map:
            if missM in link[0]:
                rq.append((link[0], link[1]))
    for link in rq:
        r2 = requests.get(link[1])
        wp = html.fromstring(r2.content)
        linksFound = wp.xpath("//a/@href")
        for ls in linksFound:
            if "download" in ls and link[0] in ls:
                res.append((link[0], ls))

    return res

def downloadFiles(mapsLinks:list, path:str, ico:str):
    """ create a new Tk() window with a progress bar and download all not found maps in 'mapsLinks' """
    try:
        pop = Tk()
        class DLPopup(ttk.Frame):
            def __init__(self, pop, **kwargs):
                ttk.Frame.__init__(self, pop, **kwargs)
                pop.title("Repair files")
                pop.iconbitmap(ico)
                pop.geometry("250x75")
                self.toplab = ttk.Label(pop, text="")
                self.toplab.pack(side=TOP)
                self.pourcent = ttk.Label(pop, text="0%")
                self.pourcent.pack(side=TOP)
                self.progress = ttk.Progressbar(pop, orient="horizontal", length=200, mode="determinate")
                self.progress.pack(side=TOP)

                self.start()

            def start(self):
                t = threading.Thread(target=self.download)
                t.daemon = True
                t.start()
                
            
            def download(self):
                for r in mapsLinks:
                    self.progress["value"] = 0
                    self.progress["maximum"] = 100
                    self.toplab["text"] = r[0]
                    wget.download(r[1], bar=self.bar, out=path)
                pop.destroy()

            def bar(self, current, total, width=100):
                self.pourcent["text"] = str(int(current / total * 100)) + "%"
                self.progress["value"] = int(current / total * 100)

        win = DLPopup(pop)
        win.mainloop()
    except Exception as e:
        showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
        pop.destroy()
        sys.exit()