try:
    import os, sys
    import requests
    import shutil
    import traceback
    from tkinter import Tk
    from tkinter.messagebox import showinfo, showerror, showwarning
    from threading import Thread
    import wget
    from zipfile import ZipFile
except ImportError as e:
    tb = sys.exc_info()[2]
    from tkinter import Tk
    Tk().withdraw()
    showerror("ImportError", "Impossible to import the libs necessary for the execution of the program.\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho" + "\n\n" + str(traceback.format_exc()))
    exit()

Tk().withdraw()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        sys.path[0] = os.path.dirname(sys.executable)
elif getattr(sys, 'frozen', False):
    sys.path[0] = sys.argv[0]
else:
    sys.path[0] = sys.argv[1]

def bar(current, total, width=100):
    os.system("cls")
    print(str(int(current / total * 100)) + "%")

try:
    path = os.path.join(sys.path[0], "epicworkshop.zip")
    wget.download("https://github.com/Naaikho/epicworkshop-compiled/archive/main.zip", bar=bar, out=path)
    
    with ZipFile(os.path.join(sys.path[0], "epicworkshop.zip")) as zf:
        for namelst in zf.filelist:
            if namelst.filename == "epicworkshop-compiled-main/Epic Workshop.exe":
                zf.extract("epicworkshop-compiled-main/Epic Workshop.exe", sys.path[0])

    if os.path.exists(os.path.join(sys.path[0], "Epic Workshop.exe")):
        os.remove(os.path.join(sys.path[0], "Epic Workshop.exe"))

    shutil.move(os.path.join(sys.path[0], "epicworkshop-compiled-main\\Epic Workshop.exe"), os.path.join(sys.path[0], "Epic Workshop.exe"))
    os.rmdir(os.path.join(sys.path[0], "epicworkshop-compiled-main"))
    os.remove(os.path.join(sys.path[0], "epicworkshop.zip"))

    if getattr(sys, 'frozen', False):
        os.execv("Epic Workshop.exe", sys.argv)
    elif __file__:
        os.chdir(sys.path[0])
        os.execv(sys.executable, [sys.executable, "epicworkshop.py"])

except KeyError:
    pass
except Exception as e:
    tb = sys.exc_info()[2]
    showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
    exit()