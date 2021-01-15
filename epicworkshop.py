
# ------------------------------------------------------------------------------------------------------------------------------------------------------------ #
#   /!\  Disclaimer: I know the code in EpicWorkshop is not optimized at all and the English of my comments is not perfect, so don't blame me for that.  /!\   #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------ #

try:
    import os, sys
    from tkinter.messagebox import showinfo, showerror, showwarning, askokcancel, askquestion, askretrycancel, askyesno
    import json
    import time
    import threading
    import requests
    from tkinter import filedialog
    from tkinter import *
    from tkinter import ttk
    from zipfile import ZipFile
    from PIL import Image, ImageTk
    import traceback
    import configparser
    import shutil
    import webbrowser
except ImportError as e:
    tb = sys.exc_info()[2]
    from tkinter import Tk
    Tk().withdraw()  # Don't show the TkInter window
    showerror("ImportError", "Impossible to import the libs necessary for the execution of the program.\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho" + "\n\n" + str(traceback.format_exc()))
    exit()


# Creating the EpicWorkshop folder in "AppData/Roaming"
try:
    if not os.path.exists(os.getenv("APPDATA") + "\\EpicWorkshop"):
        os.mkdir(os.path.join(os.getenv("APPDATA"), "EpicWorkshop"))
except Exception as e:
    showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
    exit()

def resource_path(relative_path=""):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def transformSys():
    """ Returns the path where the executed file is located """
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        path = os.path.dirname(__file__)
    return path

def appdata(f):
    """ Return the path to 'AppData/Roaming/EpicWorkshop' """
    return os.path.join(os.getenv('APPDATA') + "\\EpicWorkshop", f)

# fix the wrong path of sys.path[0]
sys.path[0] = transformSys()

# fix the bug if you have a data folder in the same folder as EpicWorkshop
try:
    if os.path.exists(os.path.join(sys.path[0], "data/")):
        shutil.copytree(os.path.join(sys.path[0], "data/"), appdata("data/"))
        shutil.rmtree(os.path.join(sys.path[0], "data/"))
except Exception:
    try:
        shutil.rmtree(os.path.join(sys.path[0], "data/"))
    except Exception:
        pass

# only works if it is opened with python:
# when you want to test the updates with epicworkshop.py you have to move epic_updater.py
# otherwise it bug with os.execv() if the path contains spaces.
try:
    if os.path.exists(sys.path[0] + "/epic_updater.py") and __file__:
        os.remove(sys.path[0] + "/epic_updater.py")
except Exception as e:
    pass

app = Tk()

class ew_app(ttk.Frame):
    def __init__(self, app, **kwargs):
        ttk.Frame.__init__(self, app, **kwargs)

        # ----------Globals Variables---------- #

        self.map_lst = {}
        self.addon_lst = {}
        self.maps_namelst = []
        self.addon_namelst = []
        self.c_map = []
        self.map_selected = []
        self.filever = "0.0.6" # actual version of EpicWorkshop
        self.ew_cfg = configparser.ConfigParser()
        self.updaterVal = True

        # ------------------------------------ #

        app.title("Epic Workshop " + self.filever)
        app.geometry("475x420")
        app.minsize(475, 400)

        #-----------------------------------------------------------------------------------------------------------#

        if getattr(sys, 'frozen', False):  # if the app is compiled
            app.iconbitmap(resource_path("epicworkshop.ico"))
        elif __file__:  # if the app is executed with python
            app.iconbitmap(sys.path[0] + "/img/epicworkshop.ico")

        #-----------------------------------------------------------------------------------------------------------#
        
        app.config(bg="#272727")

        app.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frame = Frame(app, bg="#272727", highlightthickness=0)
        self.frame.pack(fill=BOTH, anchor=CENTER, expand=YES)

        self.tmp_can = Canvas(self.frame, bg="#272727", height=40, width=200, highlightthickness=0)
        self.tmp_can.place(anchor=CENTER, relx=0.5, rely=0.6)

        self.cfg_label = Label(self.frame, text="Hi !", bg="#272727", font=("Consolas", 12), fg="white", highlightthickness=0)
        self.cfg_label.place(anchor=CENTER, relx=0.5, rely=0.5)
        
        # check if the version of the "version" file is the same as the app
        if os.path.exists(appdata("version")):
            with open(appdata("version"), "r") as data:
                ver = data.read()
            if ver != self.filever:
                patch = requests.get("https://api.github.com/repos/Naaikho/epicworkshop-compiled/releases/latest")
                patch = patch.json()["body"]
                showinfo("Patch v" + self.filever, patch)
                with open(appdata("version"), "w") as data:
                    data.write(self.filever)
        else: # or just create the "version" file
            with open(appdata("version"), "w") as data:
                data.write(self.filever)

        # start the init thread for show the live infos
        self.initthread = threading.Thread(target=self.init)
        self.initthread.daemon = True
        self.initthread.start()

    def makeUpdate(self):
        """ Start EpicWorkshopUpdate.py if the app is launch with python or .exe if compiled """

        with open(appdata("version"), "w") as data:
            data.write(self.filever)
        if getattr(sys, 'frozen', False):
            try:
                os.execv("EpicWorkshopUpdater.exe", ["\"" + sys.path[0] + "\""])
            except Exception as e:
                showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
                self.on_closing()
        elif __file__:
            shutil.copyfile(sys.path[0] + "/EpicWorkshopUpdater/epic_updater.py", "epic_updater.py")
            os.execv(sys.executable, [sys.executable, "epic_updater.py"] + ["\"" + sys.path[0] + "\""])

    def setFile(self, file, mode, put):
        import pickle
        """ Create a data file """
        with open(file, mode) as data:
            mydata = pickle.Pickler(data)
            mydata.dump(put)
            
    def getFile(self, file, mode):
        import pickle
        """ Get a data file """
        with open(file, mode) as data:
            mydata = pickle.Unpickler(data)
            return mydata.load()

    def checkForUpdate(self, arg=""):
        """ Check if EpicWorkshop have Update """
        try:
            if arg == "":
                self.cfg_label["text"] = "Check for update\n. . ."
            ver = requests.get("https://api.github.com/repos/Naaikho/epicworkshop-compiled/releases/latest")

            ver = ver.json()["tag_name"]
            
            if ver != self.filever:
                res = askyesno("Update", "New version of Epic Workshop [" + ver + "].\nDo you want to update ?", icon="info")
                if res:
                    self.makeUpdate()
                else:
                    pass
            elif arg != "":
                showinfo("v" + self.filever, "No update found.")

        except KeyError:
            if arg != "":
                showinfo("v" + self.filever, "No update found.")
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def init(self):
        """ initializing folders or create them. """
        # check for update
        self.checkForUpdate()

        try:
            self.no_path = False
            if not os.path.exists(sys.path[0] + "/map"):
                self.cfg_label["text"] = "Creating '/map'\n. . ."
                os.mkdir(sys.path[0] + "/map")

            self.cfg_label["text"] = "Check 'data/'\n. . ."
            if os.path.exists(appdata("data/")):
                self.cfg_label["text"] = "Check 'cfg.ini'\n. . ."
                if os.path.exists(appdata("data/cfg.ini")):
                    self.cfg_label["text"] = "Loading cfg.ini\n. . ."
                    self.ew_cfg.read(appdata("data\\cfg.ini"))
                    try:
                        for elm in self.ew_cfg["path"].values():
                            if not os.path.exists(elm) and elm != "":
                                self.no_path = True
                                break
                    except KeyError:
                        os.remove(appdata("data\\cfg.ini"))
                        self.no_path = True
                else:
                    self.no_path = True
            else:
                self.cfg_label["text"] = "Creating 'data/'\n. . ."
                os.mkdir(appdata("data/"))
                self.no_path = True

            if not os.path.exists(appdata("data/resources_maps")):
                self.cfg_label["text"] = "Create 'resources_maps'\n. . ."
                os.mkdir(appdata("data/resources_maps"))

            self.t1 = threading.Thread(target=self.initPathFolders)
            self.t1.daemon = True
            if self.no_path:
                self.cfg_label["text"] = "Select your platform:"
                self.ew_cfg["default"] = {}
                self.ew_cfg["path"] = {}
                self.ew_cfg["default"]["load_with_start"] = "on"
                self.ew_cfg["default"]["enable_sw"] = "on"
                self.steam_b = ttk.Button(self.tmp_can, text="Steam", command=lambda: self.setpf("steam"))
                self.steam_b.pack(side=LEFT, anchor=CENTER)
                self.tmp_sep = Canvas(self.tmp_can, bg="#272727", width=10, highlightthickness=0, height=10)
                self.tmp_sep.pack(side=LEFT, anchor=CENTER)
                self.eg_b = ttk.Button(self.tmp_can, text="Epic Games", command=lambda: self.setpf("epic games"))
                self.eg_b.pack(side=LEFT, anchor=CENTER)
            else:
                self.t1.start()

        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def setpf(self, pf:str):
        """ check if you're sure about the platform """
        self.choice = askyesno("Warn", "Select " + pf + " ?", icon="info")
        if self.choice == 0:
            pass
        else:
            self.ew_cfg['default']["platform"] = pf
            self.t1.start()



    def initPathFolders(self):
        """ ask Rocket League and Steam folder then edit or create cfg.ini """
        if self.no_path:
            self.steam_b.destroy()
            self.eg_b.destroy()
            self.tmp_sep.destroy()
            if self.ew_cfg["default"]["platform"] == "steam":
                self.cfg_label["text"] = "Select Steam folder"
                tmp_path = filedialog.askdirectory(initialdir="/", title="Select Steam folder") + "/steamapps/workshop/content/252950"
                if os.path.exists(tmp_path):
                    self.ew_cfg["path"]["steam_addons"] = tmp_path
                else:
                    self.ew_cfg["path"]["steam_addons"] = ""
            else:
                self.ew_cfg["path"]["steam_addons"] = ""
            self.cfg_label["text"] = "Select Rocket League folder"
            while 1:
                self.ew_cfg["path"]["rl_maps_folder"] = filedialog.askdirectory(initialdir="/", title="Select Rocket League folder") + "/TAGame/CookedPCConsole"
                if os.path.exists(self.ew_cfg["path"]["rl_maps_folder"]):
                    break
                else:
                    showerror("Bad path", "Please, select the Rocket League folder.")
            with open(appdata("data/cfg.ini"), "w") as cfg:
                self.ew_cfg.write(cfg)


        self.ew_cfg["path"]["origin_maps"] = appdata("data\\resources_maps")
        self.ew_cfg["path"]["custom_map_folder"] = sys.path[0] + "/map"

        # dict of maps
        # format: "InGame map name": "Map file name"
        self.map_lst = {
            "nb_maps": 44,
            "Arctagon": "ARC_P.upk",
            "Starbase": "ARC_Standard_P.upk",
            "Salty Shores Night": "Beach_Night_P.upk",
            "Salty Shores": "Beach_P.upk",
            "Forbidden Temple": "CHN_Stadium_P.upk",
            "Chamions Field Day": "CS_Day_P.upk",
            "Rivals Arena": "CS_HW_P.upk",
            "Chamions Field": "CS_P.upk",
            "Mannfield Night": "EuroStadium_Night_P.upk",
            "Mannfield": "EuroStadium_P.upk",
            "Mainnfield Rainy": "EuroStadium_Rainy_P.upk",
            "Mannfield Snow Night": "EuroStadium_SnowNight_P.upk",
            "Farmstead Night": "Farm_Night_P.upk",
            "Farmstead": "Farm_P.upk",
            "Hoops": "HoopsStadium_P.upk",
            "Labs Pillars": "Labs_CirclePillars_P.upk",
            "Labs Cosmic": "Labs_Cosmic_V4_P.upk",
            "Labs DoubleGoal": "Labs_DoubleGoal_V2_P.upk",
            "Labs Octagon": "Labs_Octagon_02_P.upk",
            "Labs Underpass": "Labs_Underpass_P.upk",
            "Labs Utopia": "Labs_Utopia_P.upk",
            "Neon Fields": "Music_P.upk",
            "Underpass": "NeoTokyo_P.upk",
            "NeoTokyo": "NeoTokyo_Standard_P.upk",
            "Park Night": "Park_Night_P.upk",
            "Park": "Park_P.upk",
            "Park Rainy": "Park_Rainy_P.upk",
            "Core 707": "ShatterShot_P.upk",
            "DFH Stadium Day": "Stadium_Day_P.upk",
            "DFH Stadium Foggy": "Stadium_Foggy_P.upk",
            "DFH Stadium": "Stadium_P.upk",
            "DFH Stadium Winter": "Stadium_Winter_P.upk",
            "Throwback Stadium": "ThrowbackStadium_P.upk",
            "Urban Central Dawn": "TrainStation_Dawn_P.upk",
            "Urban Central Night": "TrainStation_Night_P.upk",
            "Urban Central": "TrainStation_P.upk",
            "Aquadome": "Underwater_P.upk",
            "Utopia Dusk": "UtopiaStadium_Dusk_P.upk",
            "Utopia Stadium": "UtopiaStadium_P.upk",
            "Utopia Snow": "UtopiaStadium_Snow_P.upk",
            "Badland Night": "Wasteland_Night_P.upk",
            "Wasteland Night": "Wasteland_Night_S_P.upk",
            "Badland": "Wasteland_P.upk",
            "Wasteland": "Wasteland_S_P.upk"
        }
        self.cpySourceMaps()


    def cpySourceMaps(self):
        #----#    ensure that the rl maps are directly copied from the source game file    #----#

        try:
            tmp_c = os.listdir(self.ew_cfg["path"]["origin_maps"])
            self.cfg_label["text"] = "Getting maps files\n. . ."
            for elm in self.map_lst.values():
                if type(elm) == type(int()):
                    continue
                if elm not in tmp_c:
                    try:
                        self.cfg_label["text"] = "Getting maps files\n" + elm
                        shutil.copyfile(os.path.join(self.ew_cfg["path"]["rl_maps_folder"], elm), os.path.join(self.ew_cfg["path"]["origin_maps"], elm))
                    except FileNotFoundError:
                        continue
                    except Exception as e:
                        tb = sys.exc_info()[2]
                        showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
                        app.destroy()
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

        #----#    #-------------------------------------------------------------------#    #----#
        self.mapsDetector("init")

    def maps_detect(self, path:str):
        """ return a list of all '_P.upk' filenames in the path """
        mlst = os.listdir(path)
        res = []
        for itm in mlst:
            if "_P.upk" in itm:
                res.append(itm)
        return res

    def mapsDetector(self, call:str=""):
        """ check if all maps are in the rl folder and the resources_maps folder """
        try:
            map_err = []
            if call == "init":
                self.cfg_label["text"] = "Check maps files\n. . ."
            file_cnt = len(os.listdir(self.ew_cfg["path"]["origin_maps"]))

            # Check if an RL map has not been added in the 'AppData\Roaming\EpicWorkshop\data\resources_maps' folder
            for files in self.maps_detect(self.ew_cfg["path"]["origin_maps"]):
                if files not in self.map_lst.values() and "_P.upk" in files:
                    m_name = files.split("_P.")
                    self.map_lst[m_name[0]] = files

            # If a map is not in the 'resources_maps' folder, it is retrieved from the RL files
            # if the map can't be found in the RL folder, his name is recovered in the map_err list
            for files in self.map_lst.items():
                if files[1] not in self.maps_detect(self.ew_cfg["path"]["origin_maps"]) and files[0] != "nb_maps":
                    try:
                        shutil.copyfile(os.path.join(self.ew_cfg["path"]["rl_maps_folder"], files[1]), os.path.join(self.ew_cfg["path"]["origin_maps"], files[1]))
                    except FileNotFoundError:
                        map_err.append(files[0])
                elif files[1] not in self.maps_detect(self.ew_cfg["path"]["rl_maps_folder"]) and files[0] != "nb_maps":
                    map_err.append(files[0])
                
            # for all the maps not found in the RL folder, they are downloaded then put back in the folder
            if map_err != []:
                tmp_str = ""
                err_upk = []
                for elm in map_err:
                    tmp_str += "\n    - " + elm + "   ({})".format(self.map_lst[elm])
                    err_upk.append(self.map_lst[elm])
                if len(map_err) <= 1:
                    tmp_s = ["this map", "Map"]
                else:
                    tmp_s = ["these maps", "Maps"]
                res = askyesno(tmp_s[1] + " not found", "Epic Workshop was unable to find " + tmp_s[0] + ":\n" + tmp_str + "\n\nDo you want to fix it ?", icon="warning")
                if res:
                    if getattr(sys, 'frozen', False):
                        import repair
                    else:
                        from FileRepair import repair
                    rlMaps = repair.getDownloadLink(err_upk)
                    if getattr(sys, 'frozen', False):
                        ico = resource_path("epicworkshop.ico")
                    elif __file__:
                        ico = sys.path[0] + "/img/epicworkshop.ico"
                    repair.downloadFiles(rlMaps, self.ew_cfg["path"]["rl_maps_folder"], ico)
                    self.mapsDetector(call)
                    return None
                else: # if you don't want to restore your map files, the maps will just be deleted from map_lst
                    for elm in map_err:
                        del self.map_lst[elm]
                del tmp_str
                del tmp_s
            del map_err
            del file_cnt
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()
        if call == "init":
            self.getWorkshopMaps(self.ew_cfg["default"]["platform"])

    def getWorkshopMaps(self, pf:str):
        """ get all .udk and compressed maps in the 'maps' folder """
        try:
            self.addon_lst = {}
            if pf == "steam" or pf == "steam_r":
                if pf != "steam_r":
                    self.cfg_label["text"] = "Scan Steam Workshop folder\n. . ."
                no_fst = True
                for path, subdir, fileslst in os.walk(self.ew_cfg["path"]["steam_addons"]):
                    if no_fst:
                        no_fst = False
                        continue
                    for files in fileslst:
                        if ".udk" in files:
                            self.addon_lst[files.split(".")[0]] = [path, files]

            if pf != "steam_d" and pf != "steam_r":
                self.cfg_label["text"] = "Scan '/maps'\n. . ."
            compressed_lst = os.listdir(self.ew_cfg["path"]["custom_map_folder"])
            for files in compressed_lst:
                if ".zip" in files:
                    with ZipFile(self.ew_cfg["path"]["custom_map_folder"] + "/" + files, 'r') as test:
                        for names in test.filelist:
                            if ".udk" in names.filename:
                                self.addon_lst[names.filename.split(".")[0]] = [self.ew_cfg["path"]["custom_map_folder"] + "\\" + files, names.filename]
                else:
                    if ".udk" in files:
                        self.addon_lst[files.split(".")[0]] = [self.ew_cfg["path"]["custom_map_folder"], files]

        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()
        if pf != "steam_d" and pf != "steam_r":
            self.guiStart()

    def setlst(self):
        """ set graphic maps names for the combobox """
        self.addon_namelst = []
        self.maps_namelst = []

        i = 0
        for elm in self.map_lst.keys():
            if elm == "nb_maps":
                continue
            self.maps_namelst.append(elm)
            i += 1
        
        i = 0
        for elm in self.addon_lst.keys():
            self.addon_namelst.append(elm)
            i += 1
        self.maps_namelst.sort()
        self.addon_namelst.sort()

    def SWChecker(self):
        """ checks if the 'Steam Workshop Folder' checkbox is enabled and removes or re-adds Steam maps from the Addons list """
        if not self.sw_value.get():
            self.getWorkshopMaps("steam_d")
            self.setlst()
            self.addons_choice["values"] = ["Select map"] + self.addon_namelst
        else:
            self.getWorkshopMaps("steam_r")
            self.setlst()
            self.addons_choice["values"] = ["Select map"] + self.addon_namelst
    

    def tmpDestroy(self):
        """ delete the tmp file after stop the map switch """
        try:
            tmp = json.loads(self.getFile(appdata("tmp"), 'rb'))
            os.remove(os.path.join(tmp["path"], tmp["filename"]))
            shutil.copyfile(os.path.join(tmp["origin"], tmp["filename"]), os.path.join(tmp["path"], tmp["filename"]))
            os.remove(appdata("tmp"))

            self.swap_button.configure(state="normal", text="Swap", command=lambda: self.threadStarter(self.startSwap, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")), bg="#56ADD3", activebackground="#506E83", activeforeground="#D1DBE2")
            self.choice_time =True

        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def stopSwap(self):
        """ stop the map switch and restore the RL map """
        try:
            self.swap_button.configure(text=". . .", state="disable", bg="#1f1f1f")
            delete_path = os.path.join(self.ew_cfg['path']["rl_maps_folder"], self.map_selected[1])
            if os.path.exists(delete_path):
                os.remove(delete_path)
            else:
                pass
            del delete_path
            shutil.copyfile(os.path.join(self.ew_cfg["path"]["origin_maps"], self.map_selected[1]), os.path.join(self.ew_cfg['path']["rl_maps_folder"], self.map_selected[1]))

            os.remove(appdata("tmp"))

            self.swap_button.configure(state="normal", text="Swap", command=lambda: self.threadStarter(self.startSwap, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")), bg="#56ADD3", activebackground="#506E83", activeforeground="#D1DBE2")
            self.choice_time =True
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def startSwap(self):
        """ swap the workshop map in 'c_map' with the RL map contain in 'map_selected' """
        try:
            self.choice_time = False

            self.c_map = self.addons_choice.get()
            self.map_selected = self.maps_choice.get()

            self.c_map = [self.c_map, self.addon_lst[self.c_map]]
            self.map_selected = [self.map_selected, self.map_lst[self.map_selected]]

            # delete the map in rl path
            delete_path = os.path.join(self.ew_cfg['path']["rl_maps_folder"], self.map_selected[1])
            if os.path.exists(delete_path):
                os.remove(delete_path)
            else:
                showwarning("Oof", "Not map found.")
                return None

            # copy the custom map to the rl path (or extract)
            if ".zip" in self.c_map[1][0]:
                with ZipFile(self.c_map[1][0]) as zf:
                    zf.extract(self.c_map[1][1], self.ew_cfg["path"]["rl_maps_folder"])
                    os.rename(os.path.join(self.ew_cfg["path"]["rl_maps_folder"], self.c_map[1][1]), os.path.join(self.ew_cfg["path"]["rl_maps_folder"], self.map_selected[1]))
            else:
                shutil.copyfile(os.path.join(self.c_map[1][0], self.c_map[1][1]), os.path.join(self.ew_cfg["path"]["rl_maps_folder"], self.map_selected[1]))

            # create the 'tmp' file
            status = {
                "filename": self.map_selected[1],
                "path": self.ew_cfg["path"]["rl_maps_folder"],
                "origin": self.ew_cfg["path"]["origin_maps"]
                }
            self.setFile(appdata("tmp"), "wb", json.dumps(status, indent=4))
            del status

            self.swap_button.configure(state="normal", text="Stop", bg="#D35682", activebackground="#835057", activeforeground="#E2D1D4", command=lambda: self.threadStarter(self.stopSwap, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")))

        except PermissionError:
            showerror("Can't replace '" + self.map_selected[1] + "'", "Error: " + self.map_selected[1] + " cannot currently be replaced\nGo to the " + self.map_selected[0] + " map in free play then try again.")
            self.swap_button.configure(state="normal", text="Swap", command=lambda: self.threadStarter(self.startSwap, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")), bg="#56ADD3", activebackground="#506E83", activeforeground="#D1DBE2")
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def reloadMaps(self):
        """ function for reload button """
        self.mapsDetector()
        self.SWChecker()

    def threadButton(self, button, state, text, bg, activebackground="", activeforeground="", command=""):
        """ change the states of the 'button' """
        if activebackground == "":
            activebackground = button["activebackground"]
        if activeforeground == "":
            activeforeground = button["activeforeground"]
        if command == "":
            command = button["command"]
        button.configure(state=state, text=text, bg=bg, activebackground=activebackground, activeforeground=activeforeground, command=command)

    def threadStarter(self, cmd, button):
        """ start a thread with 'cmd' and 'button' lambda function """
        tmp_t = threading.Thread(target=cmd)
        tmp_b = threading.Thread(target=button)
        tmp_t.daemon = True
        tmp_b.daemon = True
        tmp_t.start()
        tmp_b.start()

    def startUptade(self):
        """ work like the unity update function | check all conditions every 0.1 sec """
        tmp_norepeat = ""
        try:
            while self.updaterVal:
                if self.choice_time:
                    # check if a RL map and a Addon has been selected and enable the "Swap" button if it is
                    if self.maps_choice.get() != "Select map" and self.maps_choice.get() in self.maps_namelst and self.addons_choice.get() != "Select addon" and self.addons_choice.get() in self.addon_namelst:
                        if self.swap_button["state"] == "disabled":
                            self.swap_button.configure(state="normal", bg="#56ADD3")
                    elif self.swap_button["state"] == "normal":
                        self.swap_button.configure(state="disable", bg="#1f1f1f")
                # see if there is an image in the same path as the map.udk and display it if it finds it
                if tmp_norepeat != self.addons_choice.get():
                    tmp_norepeat = self.addons_choice.get()
                    if self.addons_choice.get() in self.addon_lst.keys():
                        tmp_path = self.addon_lst[self.addons_choice.get()]
                        tmp_img_name = ""
                        from io import BytesIO
                        if ".zip" in tmp_path[0]:
                            with ZipFile(tmp_path[0]) as zf:
                                for name in zf.filelist:
                                    if ".png" in name.filename or ".jpg" in name.filename or ".jpeg" in name.filename:
                                        tmp_img_name = name.filename
                                        break
                                if tmp_img_name != "":
                                    data = zf.read(tmp_img_name)
                                    dataEnc = BytesIO(data)
                                    tmp_img = Image.open(dataEnc)
                                    tmp_img = tmp_img.resize((128*2, 72*2), Image.ANTIALIAS)
                                    tmp_img = ImageTk.PhotoImage(tmp_img)
                                    self.map_img.itemconfig(self.img_id, image=tmp_img)
                                else:
                                    if getattr(sys, 'frozen', False):
                                        tmp_img = Image.open(resource_path("no_img.png"))
                                    else:
                                        tmp_img = Image.open(os.path.join(sys.path[0], "img\\no_img.png"))
                                    tmp_img = tmp_img.resize((128*2, 72*2), Image.ANTIALIAS)
                                    tmp_img = ImageTk.PhotoImage(tmp_img)
                                    self.map_img.itemconfig(self.img_id, image=tmp_img)
                        else:
                            for img in os.listdir(tmp_path[0]):
                                if ".png" in img or ".jpg" in img or ".jpeg" in img:
                                    tmp_img_name = img
                                    break
                            if tmp_img_name != "":
                                tmp_img = Image.open(os.path.join(tmp_path[0], tmp_img_name))
                                tmp_img = tmp_img.resize((128*2, 72*2), Image.ANTIALIAS)
                                tmp_img = ImageTk.PhotoImage(tmp_img)
                                self.map_img.itemconfig(self.img_id, image=tmp_img)
                            else:
                                if getattr(sys, 'frozen', False):
                                    tmp_img = Image.open(resource_path("no_img.png"))
                                else:
                                    tmp_img = Image.open(os.path.join(sys.path[0], "img\\no_img.png"))
                                tmp_img = tmp_img.resize((128*2, 72*2), Image.ANTIALIAS)
                                tmp_img = ImageTk.PhotoImage(tmp_img)
                                self.map_img.itemconfig(self.img_id, image=tmp_img)
                    else:
                        if getattr(sys, 'frozen', False):
                            tmp_img = Image.open(resource_path("no_img.png"))
                        else:
                            tmp_img = Image.open(os.path.join(sys.path[0], "img\\no_img.png"))
                        tmp_img = tmp_img.resize((128*2, 72*2), Image.ANTIALIAS)
                        tmp_img = ImageTk.PhotoImage(tmp_img)
                        self.map_img.itemconfig(self.img_id, image=tmp_img)
                time.sleep(0.1)
        except TclError:
            pass

    def openFolder(self, path):
        """ open the 'path' in explorer """
        import subprocess
        subprocess.Popen('explorer {}'.format(path))
    
    def resetSett(self):
        """ reset app settings (delete '\AppData\Roaming\EpicWorkshop\cfg.ini') """
        res = askyesno("Reset settings", "All app settings will be deleted (your maps will not be affected).\nContinue ?")
        if res:
            self.updaterVal = False
            self.frame.destroy()
            settings = appdata("data/")
            if os.path.exists(settings):
                os.remove(os.path.join(settings, "cfg.ini"))
            # reload the app
            self.__init__(app)

    def guiStart(self):
        """ set the main app GUI """
        try:
            self.tmp_can.destroy()
            self.cfg_label.destroy()
            self.setlst()
            self.sw_value = BooleanVar()
            self.lws = BooleanVar()
            self.choice_time =True
            self.updaterVal = True

            self.frame.destroy()
            self.frame = Frame(app, bg="#272727", highlightthickness=0)
            self.frame.pack(fill=BOTH, anchor=CENTER, expand=YES)

            self.options = Canvas(self.frame, bg="#272727", height=50, width=150, highlightthickness=0)
            self.steam_detect = Checkbutton(self.options, text="Steam Workshop folder", command=self.SWChecker, onvalue="on", offvalue="off", variable=self.sw_value, font=("Franklin Gothic Medium", 8), selectcolor="#272727", relief="flat", activeforeground="white", fg="white", bg="#272727", bd=0, highlightthickness=0, activebackground="#272727")
            self.sc = Canvas(self.options, bg="#272727", width=15, height=0, highlightthickness=0)
            self.load_w_start = Checkbutton(self.options, text="Load maps with Start", onvalue="on", offvalue="off", variable=self.lws, font=("Franklin Gothic Medium", 8), selectcolor="#272727", relief="flat", activeforeground="white", fg="white", bg="#272727", bd=0, highlightthickness=0, activebackground="#272727")

            self.s1 = Canvas(self.frame, bg="#272727", height=25, highlightthickness=0)

            self.choice_can = Canvas(self.frame, height=100, width=350, highlightthickness=0)
            self.l_selec = Canvas(self.choice_can, bg="#272727", height=50, width=175, highlightthickness=0)
            self.r_selec = Canvas(self.choice_can, bg="#272727", height=50, width=175, highlightthickness=0)

            self.s2 = Canvas(self.frame, bg="#272727", height=15, highlightthickness=0)
            self.s3 = Canvas(self.frame, bg="#272727", height=25, highlightthickness=0)
            self.s4 = Canvas(self.frame, bg="#272727", height=15, highlightthickness=0)

            self.img_frame = Frame(self.frame, bg="#272727", highlightthickness=0)

            #-----------------------------------------------------------------------------------------------------------#

            if getattr(sys, 'frozen', False):
                self.img = Image.open(resource_path("no_img.png"))
            elif __file__:
                self.img = Image.open(os.path.join(sys.path[0], "img\\no_img.png"))

            #-----------------------------------------------------------------------------------------------------------#

            self.img = self.img.resize((128*2, 72*2), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.img)
            self.map_img = Canvas(self.img_frame, bg="#171717", height=72*2, width=128*2, highlightthickness=0)
            self.img_id = self.map_img.create_image((128, 72), image=self.img)
            self.map_img.grid(row=0, column=0, sticky=N)
            self.buttons = Canvas(self.frame, bg="#272727", height=50, highlightthickness=0)

            self.swap_button = Button(self.buttons, command=lambda: self.threadStarter(self.startSwap, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")), text="Swap", font=("Franklin Gothic Medium", 20), disabledforeground="#272727", fg="White", bg="#56ADD3", width=30, bd=0, activebackground="#506E83", highlightthickness=0, activeforeground="#D1DBE2")
            self.sb = Canvas(self.frame, height=9, bg="#272727", bd=0, highlightthickness=0)

            self.maps_label = Label(self.l_selec, text="Select a Rocket league map:", font=("Franklin Gothic Medium", 8), fg="white", bg="#272727", highlightthickness=0)
            self.addons_label = Label(self.r_selec, text="Select a Workshop map:", font=("Franklin Gothic Medium", 8), fg="white", bg="#272727", highlightthickness=0)


            self.maps_choice = ttk.Combobox(self.l_selec, values=["Select map"] + self.maps_namelst)
            self.addons_choice = ttk.Combobox(self.r_selec, values=["Select addon"] + self.addon_namelst)

            self.choice_sep = Canvas(self.choice_can, bg="#272727", width=50, height=50, highlightthickness=0)
            self.filesreload = ttk.Button(self.frame, text="Reload files", width=20, command=self.reloadMaps)

            self.maps_choice.current(0)
            self.addons_choice.current(0)

            self.MENUbar = Menu(app)
            self.file = Menu(self.MENUbar, tearoff=0)
            self.file.add_command(label="Open Epic Workshop folder", command=lambda: self.openFolder(sys.path[0]))
            self.file.add_command(label="Open Epic Workshop data folder", command=lambda: self.openFolder(appdata("")))
            self.file.add_command(label="Reset settings", command=self.resetSett)
            self.file.add_command(label="Check for update", command=lambda: self.checkForUpdate("cmd"))
            self.download = Menu(self.MENUbar, tearoff=0)
            self.download.add_command(label="Find a Workshop map", command=lambda: webbrowser.open("https://steamcommunity.com/workshop/browse/?appid=252950&browsesort=trend&section=readytouseitems"))
            self.download.add_command(label="Map downloader", command=lambda: webbrowser.open("https://steamworkshopdownloader.io/"))
            self.links = Menu(self.MENUbar, tearoff=0)
            self.links.add_command(label="Epic Workshop Discord", command=lambda: webbrowser.open("https://discord.gg/zEEVSewWSP"))
            self.links.add_command(label="Help", command=lambda: webbrowser.open("https://github.com/Naaikho/epicworkshop-compiled/blob/main/README.md"))
            self.links.add_command(label="Donation", command=lambda: webbrowser.open("https://www.paypal.com/paypalme/naikho"))
            self.credits = Menu(self.MENUbar, tearoff=0)
            self.credits.add_command(label="Naikho", command=lambda: webbrowser.open("https://linkmix.co/2059499"))
            self.MENUbar.add_cascade(label="Files", menu=self.file)
            self.MENUbar.add_cascade(label="Downloads", menu=self.download)
            self.MENUbar.add_cascade(label="Links", menu=self.links)
            self.MENUbar.add_cascade(label="Credits", menu=self.credits)

            self.maps_label.place(anchor=CENTER, relx=0.5, rely=0.25)
            self.addons_label.place(anchor=CENTER, relx=0.5, rely=0.25)

            self.maps_choice.place(anchor=CENTER, relx=0.5, rely=0.8)
            self.addons_choice.place(anchor=CENTER, relx=0.5, rely=0.8)

            self.s1.pack(fill=X, side=TOP)
            self.options.pack(anchor=CENTER, side=TOP)
            self.steam_detect.pack(anchor=CENTER, side= LEFT)
            self.sc.pack(anchor=CENTER, side= LEFT)
            self.load_w_start.pack(anchor=CENTER, side= LEFT)

            self.s2.pack(fill=X, side=TOP)

            self.choice_can.pack(side=TOP, anchor=CENTER)
            self.l_selec.pack(side=LEFT, anchor=CENTER)
            self.choice_sep.pack(side=LEFT, anchor=CENTER)
            self.r_selec.pack(side=LEFT, anchor=CENTER)

            self.s3.pack(side=TOP)
            self.filesreload.pack(anchor=CENTER)
            self.s4.pack(side=TOP)
            self.img_frame.pack(side=TOP, anchor=CENTER)
            self.swap_button.pack(fill=BOTH, side=LEFT, anchor=CENTER)
            self.swap_button.configure(state="disable", bg="#1f1f1f")
            self.sb.pack(fill=X, anchor=CENTER, side=BOTTOM)
            self.buttons.pack(anchor=CENTER, side=BOTTOM)
            app.config(menu=self.MENUbar)

            # --------- # get and set the parameters saved when closing the app # --------- #
            
            if self.ew_cfg["default"]["load_with_start"] == "on":
                self.load_w_start.select()
            else:
                self.load_w_start.deselect()

            if self.ew_cfg["path"]["steam_addons"] == "":
                self.steam_detect.deselect()
                self.steam_detect.configure(state="disabled")
            else:
                if self.ew_cfg["default"]["enable_sw"] == "on":
                    self.steam_detect.select()
                    self.SWChecker()
                else:
                    self.steam_detect.deselect()
                    self.SWChecker()

            # security for the update with the tmp file
            if os.path.exists(os.path.join(sys.path[0], "tmp")):
                shutil.move(os.path.join(sys.path[0], "tmp"), appdata("tmp"))

            self.resourcetmp = appdata("tmp")
            if os.path.exists(self.resourcetmp):
                self.choice_time = False
                self.swap_button.configure(state="normal", text="Stop", bg="#D35682", activebackground="#835057", activeforeground="#E2D1D4", command=lambda: self.threadStarter(self.tmpDestroy, lambda: self.threadButton(button=self.swap_button, text=". . .", state="disable", bg="#1f1f1f")))
            
            # --------- # ----------------------------------------------------- # --------- #

            self.t2 = threading.Thread(target=self.startUptade)
            self.t2.daemon = True
            self.t2.start()
        except Exception as e:
            showerror(str(type(e)), str(traceback.format_exc()) + "\n\nReport:\n    Email: naikho@naikho.com\n    Twitter: @naaikho")
            self.on_closing()

    def finishThread(self):
        """ release last task in threading subprocess after closing (remove all maps in the resources_maps path excepted the currently swaped map) """
        if not self.choice_time:
            for files in os.listdir(self.ew_cfg["path"]["origin_maps"]):
                if files != self.map_selected[1]:
                    os.remove(os.path.join(self.ew_cfg["path"]["origin_maps"], files))
        else:
            for files in os.listdir(self.ew_cfg["path"]["origin_maps"]):
                os.remove(os.path.join(self.ew_cfg["path"]["origin_maps"], files))

    def on_closing(self):
        """ set new settings and last tasks before closing """
        try:
            endt = threading.Thread(target=self.finishThread)
            if self.lws.get():
                endt.start()
                self.ew_cfg["default"]["load_with_start"] = "on"
            else:
                self.ew_cfg["default"]["load_with_start"] = "off"
            if self.sw_value.get():
                self.ew_cfg["default"]["enable_sw"] = "on"
            else:
                self.ew_cfg["default"]["enable_sw"] = "off"
            with open(appdata("data/cfg.ini"), "w") as cfg:
                self.ew_cfg.write(cfg)
        except Exception:
            pass
        app.destroy()



starter = ew_app(app)
starter.mainloop()