import subprocess
import sys
import os
import os.path
import pathlib
from contextlib import redirect_stderr, redirect_stdout
import difflib
import logging

import shutil

import threading
import urllib.request
import zipfile
from os import path
from zipfile import ZipFile
import pkg_resources


import_list = {"requests","wget","PyQt5","tqdm"}
if os.path.exists("sys/pyinstalled") == False:
    for module in import_list:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            with open("sys/pyinstalled", mode='a'): pass
        except:
            pass
else:
    pass

import requests
import wget
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QMessageBox,
    QCheckBox,
)
from tqdm.auto import tqdm
import shlex

defpath = os.getcwd()
processing = False
only_update = False
new_install = True
updatefiles = 0
#sys.stdout = open(os.devnull, "w")
#sys.stderr = open(os.devnull, "w")
gamemode = False

class downloadNewThread(QThread):
    data_downloaded = Signal(object)
    perc_downloaded = Signal(object)
    current_link = Signal(object)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):

        pass

    def run(self):
        try:
            try:
                os.remove("sys/update")
            except:
                pass
            with open("sys/defaultfiles") as f1:
                f1_text = f1.readlines()
            with open("sys/files") as f2:
                f2_text = f2.readlines()
            update_file = open("sys/update", "w")
            f2.close()

            # Find and print the diff:
            for line in difflib.unified_diff(f1_text, f2_text):
                if line[0] == "+" and line[1] != "+":
                    print(line)
                    n = update_file.write(line)
            update_file.close()
        except:
            e = sys.exc_info()[0]
            msg = QMessageBox()
            msg.setText(str(e))
            msg.exec_()
        filearray = []
        f = open("sys/update")
        line = f.readline()
        while line:
            linePart = line.partition(">")[0].replace("\\", "/").replace("+", "")
            # window["status"].update("Downloading...")
            filearray.append(linePart)
            line = f.readline()
        for item in filearray:
            print(filearray.index(item))
            self.current_link.emit(item)
            download(item, self.perc_downloaded)
            self.data_downloaded.emit(filearray.index(item) * 73 / 100)
        filesurl = "http://update.poke.one/files"
        urllib.request.urlretrieve(filesurl, "sys/defaultfiles")
        self.isFinished = True


class downloadThread(QThread):
    data_downloaded = Signal(object)
    perc_downloaded = Signal(object)
    current_link = Signal(object)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):

        pass

    def run(self):
        error = False
        filearray = []
        filesurl = "http://update.poke.one/files"
        try:
            os.remove("sys/files")
        except Exception as e:
            print(e)
        if error == False:
            urllib.request.urlretrieve(filesurl, "sys/files")
            f = open("sys/files")
            line = f.readline()
            while line:
                linePart = line.partition(">")[0].replace("\\", "/")
                # window["status"].update("Downloading...")
                filearray.append(linePart)
                line = f.readline()
            for item in filearray:
                print(filearray.index(item))
                self.current_link.emit(item)
                download(item, self.perc_downloaded)
                self.data_downloaded.emit(filearray.index(item))
            try:
                os.remove("sys/defaultfiles")
            except:
                pass
            shutil.copyfile("sys/files", "sys/defaultfiles")
        error = False
        self.isFinished = True


class extractThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):

        pass

    def run(self):
        error = False
        rootpath = pathlib.Path().absolute()
        print(rootpath)
        global currentfile
        count = 0
        # error check
        try:
            with open("sys/files", "r") as f:
                pass
        except Exception as e:
            print(e)
            error = True
        if error == False:
            if only_update == False:
                with open("sys/files", "r") as f:
                    for line in f:
                        count += 1
            else:
                with open("sys/update", "r") as f:
                    for line in f:
                        count += 1
            try:
                print(currentfile)
                try:
                    for root, dirs, files in os.walk(rootpath):
                        for name in files:
                            if name.endswith((".zip", ".ZIP")):
                                print(
                                    "Extracting file from Archive: "
                                    + str(os.path.join(root, name))
                                )
                                path = pathlib.Path(os.path.join(root, name))
                                print(path.parent)
                                os.chdir(path.parent)
                                file_name = name  # get full path of files
                                print(file_name)
                                try:
                                    zip_ref = zipfile.ZipFile(
                                        path
                                    )  # create zipfile object
                                    zip_ref.extractall()  # extract file to dir
                                    zip_ref.close()  # close file
                                    os.remove(file_name)  # delete zipped file
                                    currentfile += 1
                                    # window['progress'].update_bar(currentfile / count * 100)
                                except Exception as e:
                                    print(e)
                    os.chdir(rootpath)
                except Exception as e:
                    print(e)
                    os.chdir(rootpath)
            except:
                pass
        error = False


class Launcher(QWidget):
    def __init__(self):
        super(Launcher, self).__init__()
        createFiles()
        self.setup()
        # self.center()
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # self.oldPos = self.pos()
        self.show()
        if path.exists("sys/installed"):
            print("not a new install")
            new_install = False
        else:
            print("is a new install")
            new_install = True
            msg_u = QMessageBox()
            msg_u.setWindowTitle("Warning!")
            msg_u.setText(
                "This is not official Software. It might not work as excpected!"
            )
            msg_u.exec()

        open("sys/installed", "a").close()
        if new_install == True:
            self.goself()
        else:
            self.checknew()

    def import_all(self):
        pass

    def goself(self):
        try:
            os.remove("sys/files")
        except:
            pass
        self.btn_go.setEnabled(False)
        #self.btn_r.setEnabled(False)
        self.btn_c.setEnabled(False)
        self.btn_launch.setEnabled(False)
        self.threads = []
        downloader = downloadThread()
        downloader.data_downloaded.connect(self.on_data_ready)
        downloader.perc_downloaded.connect(self.updateperc)
        downloader.current_link.connect(self.updateLabel)
        downloader.finished.connect(self.on_finished_down)
        self.threads.append(downloader)
        downloader.start()

    def checknew(self):
        self.btn_go.setEnabled(False)
        #self.btn_r.setEnabled(False)
        self.btn_c.setEnabled(False)
        self.btn_launch.setEnabled(False)
        self.threads = []
        downloader1 = downloadNewThread()
        downloader1.data_downloaded.connect(self.on_data_ready)
        downloader1.perc_downloaded.connect(self.updateperc)
        downloader1.current_link.connect(self.updateLabel)
        downloader1.finished.connect(self.on_finished_down)
        self.threads.append(downloader1)
        downloader1.start()

    def on_finished_down(self):
        str1 = "Extracting..."
        self.updateLabel(str1)
        extractor = extractThread()
        self.threads.append(extractor)
        extractor.finished.connect(self.on_finished_ex)
        extractor.start()

    def on_finished_ex(self):
        self.btn_go.setEnabled(True)
        # self.btn_x.setEnabled(True)
        self.btn_c.setEnabled(True)
        #self.btn_r.setEnabled(True)
        self.btn_launch.setEnabled(True)
        self.progressfile.setValue(100)
        self.progressall.setValue(73)
        self.label_curr.setText("Finished!")

    def on_data_ready(self, data):
        print(data)
        self.progressall.setValue(data)

    def updateperc(self, data):
        print(data)
        self.progressfile.setValue(data)

    def updateLabel(self, data):
        self.label_curr.setText(data)

    def launchGame(self):
        try:
            subprocess.Popen("start gamedata/PokeOne.exe")
        except Exception as e:
            print(e)
        try:
            if gamemode == True:
                subprocess.Popen("DXVK_ASYNC=1 gamemoderun wine gamedata/PokeOne.exe", shell=True)
            else:
                subprocess.Popen("wine gamedata/PokeOne.exe", shell=True)

        except Exception as e:
            print(e)

    def changelogEvent(self):
        msg = QMessageBox()
        msg.setWindowTitle("Launcher Changelog")
        msg.setText("v2.2.3-S: Removed Reload Button.")
        msg.exec()

    def reloadEvent(self):
        cmd = "python " + defpath + "/main-simple.py"
        cmds = shlex.split(cmd)
        p = subprocess.Popen(cmds, start_new_session=True)
        sys.exit()
    def clickChBox(self, state):

        if state == QtCore.Qt.Checked:
            print('Checked')
            gamemode = True
            with open('sys/gm', 'w'): pass
        else:
            print('Unchecked')
            gamemode = False
            os.remove('sys/gm')
    def setup(self):

        vbox = QVBoxLayout(self)
        # self.webEngineView = QWebEngineView()
        # self.loadPage()
        # self.btn_x = QPushButton('X', self)
        # self.btn_x.resize(40,30)
        # self.btn_x.move(700-42,0+2)
        # self.btn_x.clicked.connect(self.closeEvent)

        self.btn_c = QPushButton("Changelog", self)
        #self.btn_c.resize(200, 30)
        self.btn_c.resize(0, 0)
        # self.btn_c.move(700-264,0+2)
        self.btn_c.clicked.connect(self.changelogEvent)

        #self.btn_r = QPushButton("Reload", self)
        #self.btn_r.resize(150, 30)
        #self.btn_r.move(700 - 264 - 250, 0)
        #self.btn_r.clicked.connect(self.reloadEvent)

        #self.labelupd = QLabel("<-- Click to recheck for updates", self)
        #self.labelupd.resize(250, 30)
        #self.labelupd.move(700 - 264 - 100, 0)

        self.btn_go = QPushButton("Full Download", self)
        self.btn_go.clicked.connect(self.goself)
        self.btn_go.resize(80, 20)
        self.btn_go.move(700 - 66 - 80, 0 + 2)
        self.btn_launch = QPushButton("Launch", self)
        self.btn_launch.clicked.connect(self.launchGame)
        self.btn_launch.resize(675, 90)
        self.btn_launch.move(13, 315)
        self.label_curr = QLabel("")
        self.label_progress = QLabel("Progress:")
        self.progressfile = QProgressBar(self)
        self.progressfile.setGeometry(0, 0, 300, 25)
        self.progressfile.setMaximum(100)
        self.progressall = QProgressBar(self)
        self.progressall.setGeometry(0, 0, 300, 25)
        self.progressall.setMaximum(73)
        self.Spacer = QtWidgets.QSpacerItem(20, 20)

        # add labels to vbox after here
        vbox.addItem(self.Spacer)
        # vbox.addWidget(label_title)

        # vbox.addWidget(self.webEngineView)

        # vbox.addItem(self.Spacer)
        # vbox.addItem(self.Spacer)
        # vbox.addItem(self.Spacer)
        # vbox.addItem(self.Spacer)
        # vbox.addItem(self.Spacer)
        self.chbox = QCheckBox("With Gamemode (on Linux)",self)
        self.chbox.resize(160,30)
        self.chbox.stateChanged.connect(self.clickChBox)
        if os.path.exists("sys/gm"):
            self.chbox.setChecked(True)
        else:
            pass
        
        vbox.addWidget(self.label_curr)
        vbox.addWidget(self.progressfile)
        vbox.addWidget(self.label_progress)
        vbox.addWidget(self.progressall)
        vbox.addWidget(self.btn_go)
        vbox.addWidget(self.btn_launch)
        vbox.addWidget(self.chbox)
        
        self.setLayout(vbox)
        self.setGeometry(100, 100, 200, 150)
        self.setFixedSize(700, 220)
        self.setWindowTitle("PokeOne Launcher V2")

filearray = []
thread_finished = threading.Event()
result_available = threading.Event()


def download_thread(
    self,
    arg1,
):
    for item in arg1:
        # print(item)
        download(item, self)
        # window['p_t'].update_bar(0)
        pass
    thread_finished.set()


def runUpdate(
    self,
    only_update=False,
):
    if only_update == False:
        parseUpdate(
            self,
        )
    else:
        parseUpdate(self, only_update=True)
    nop = None
    cmd = ""
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = ""
    for line in p.stdout:
        line = line.decode(
            errors="replace" if (sys.version_info) < (3, 5) else "backslashreplace"
        ).rstrip()
        output += line

    retval = p.wait(40)
    result_available.set()
    return (retval, output)


def parseUpdate(self, only_update=False, update_file=""):
    if only_update == False:

        filesurl = "http://update.poke.one/files"
        urllib.request.urlretrieve(filesurl, "sys/files")
        f = open("files")
        line = f.readline()
        while line:
            linePart = line.partition(">")[0].replace("\\", "/")
            # window["status"].update("Downloading...")
            filearray.append(linePart)
            line = f.readline()
        t = threading.Thread(
            target=download_thread,
            args=(
                self,
                filearray,
            ),
            daemon=True,
        )
        t.start()
        thread_finished.wait()
        f.close()
    else:
        filesurl = "http://update.poke.one/files"
        urllib.request.urlretrieve(filesurl, "files")
        f = open("update")
        line = f.readline()
        while line:
            linePart = line.partition(">")[0].replace("\\", "/").replace("+", "")
            # window["status"].update("Downloading...")
            filearray.append(linePart)
            line = f.readline()
        t = threading.Thread(target=download_thread, args=(filearray,), daemon=True)
        t.start()
        thread_finished.wait()
        f.close()


def update_thread(
    self,
    only_update=False,
):
    if only_update == False:
        runUpdate(self)
        result_available.wait()
        extractFile(self, only_update=False)
    else:
        runUpdate(self, only_update=True)
        result_available.wait()
        extractFile(self, only_update=True)
        try:
            os.remove("sys/defaultfiles")
        except:
            pass
        try:
            shutil.copy("sys/files", "sys/defaultfiles")
        except:
            with open("sys/files") as fg:
                with open("sys/files") as fg2:
                    fg.write(fg2.read())
            fg.close()
            shutil.copy("sys/files", "sys/defaultfiles")
    # window["status"].update("Finished!")
    # window['progress'].update_bar(100)
    updating = False


def download(file, percobj):
    downloadString = ("http://update.poke.one/request/" + file).replace(" ", "%20")
    try:
        req = urllib.request.Request(downloadString, method="HEAD")
        r = urllib.request.urlopen(req)
        outputfile = downloadString.replace("http://update.poke.one/request/", "")
        outputfile = "gamedata/" + outputfile + ".zip"
        print(outputfile)
        # num_lines = sum(1 for line in open('files'))
        global currentfile
        currentfile = 0
        count = 0
        currentfile += 1
        response = requests.get(downloadString, stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        block_size = 32 * 1024  # 1 Kibibyte
        progress_bar = tqdm(
            total=total_size_in_bytes, unit="iB", unit_scale=True, disable=False
        )
        with open(outputfile, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                percobj.emit(round(progress_bar.n / total_size_in_bytes * 100))
                # self.progressfile.setValue(
                #   round(progress_bar.n/total_size_in_bytes*100))
                file.write(data)
        # f2 = open(outputfile, "wb").write(response.content)
        # window['progress'].update_bar(currentfile / count * 100)
    except:
        e = sys.exc_info()[0]
        msg = QMessageBox()
        msg.setText(str(e))
        msg.exec_()


def checkupdates():
    import difflib

    print("running check")
    try:
        try:
            os.remove("sys/update")
        except:
            pass
        with open("sys/defaultfiles") as f1:
            f1_text = f1.readlines()
        with open("sys/files") as f2:
            f2_text = f2.readlines()
        update_file = open("sys/update", "w")
        f2.close()

        # Find and print the diff:
        for line in difflib.unified_diff(f1_text, f2_text):
            if line[0] == "+" and line[1] != "+":
                print(line)
                n = update_file.write(line)
        update_file.close()
    except:
        e = sys.exc_info()[0]
        msg = QMessageBox()
        msg.setText(str(e))
        msg.exec_()





def createFiles():
    try:
        if path.exists("gamedata/") == False:
            os.mkdir("gamedata/")
        os.makedirs("gamedata/PokeOne_Data/StreamingAssets/", exist_ok=True)
        os.makedirs("gamedata/PokeOne_Data/Resources/", exist_ok=True)
        os.makedirs("gamedata/PokeOne_Data/Plugins/", exist_ok=True)
        os.makedirs("gamedata/PokeOne_Data/il2cpp_data/Resources/", exist_ok=True)
        os.makedirs("gamedata/PokeOne_Data/il2cpp_data/Metadata/", exist_ok=True)
        os.makedirs(
            "gamedata/PokeOne_Data/il2cpp_data/etc/mono/mconfig/", exist_ok=True
        )
        os.makedirs(
            "gamedata/PokeOne_Data/il2cpp_data/etc/mono/4.5/Browsers/", exist_ok=True
        )
        os.makedirs(
            "gamedata/PokeOne_Data/il2cpp_data/etc/mono/4.0/Browsers/", exist_ok=True
        )
        os.makedirs(
            "gamedata/PokeOne_Data/il2cpp_data/etc/mono/2.0/Browsers/", exist_ok=True
        )

        if path.exists("sys/") == False:
            os.mkdir("sys/")

        if path.exists("sys/defaultfiles") == False:
            wget.download("http://update.poke.one/files", out="sys/defaultfiles")
        if path.exists("sys/files") == False:
            wget.download("http://update.poke.one/files", out="sys/files")

    except:
        pass
    # wget.download("http://update.poke.one/notice",out="sys/notice.html")
app = QApplication(sys.argv)
# app.setStyleSheet(qdarkstyle.load_stylesheet())
tqdm.monitor_interval = 0
launchWin = Launcher()

sys.exit(app.exec_())

if __name__ == "__main__":
    # with open('errorlog.txt', 'w') as out:
    #    with redirect_stdout(out):
    #     run()#
    run()
