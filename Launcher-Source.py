import os
import subprocess
import sys
import urllib.request
import zipfile
from zipfile import ZipFile
from time import sleep
import pathlib
import PySimpleGUI as sg
import requests
import wget
import platform
from GrabzIt import GrabzItClient
from PIL import Image



sg.theme('DarkTanBlue')
currentfile = 0
options = {
    'format': 'png',
    'crop-h': '300',
    'encoding': "UTF-8",
}

def main():
    if os.path.exists("./PokeOne_Data/") == False:
        sg.Popup('No data Folder found. Please extract all Files form your downloaded Archive!', keep_on_top=True,title="Error")
        window.close()
    layout = [
        [sg.Image("./notice.png",key="-image-",background_color="#FFF")],
        [sg.Output(size=(145, 20), background_color='black', text_color='white')],
        [sg.ProgressBar(max_value=100, orientation='h', size=(60, 20), key='progress'), sg.Text(text="", key="totalfiles", size=(3, 1)), sg.Text(text="", key="count", size=(8, 1))],
        [sg.Button("Launch"), sg.Button('Update'),sg.Button('Update News'), sg.Button('Exit'), sg.Text(text="", key="status", size=(16, 1))]]
    window = sg.Window('PokeOne Updater - written in Python3',layout, finalize=True)
    updating = False
    try:
        window["-image-"].update("./notice_online.jpg")
    except:
        window["-image-"].update("./notice.png")
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == "Update News":
            try:
                os.remove("./notice_online.jpg")
            except:
                pass
            try:
                
                grabzIt = GrabzItClient.GrabzItClient("YTNlN2ViZTJiYjkxNGU0Mjg1ZGE5ZDBjZTgwZDMwNGY=", "SUM/Pz8/DT9HPxY/Pz9+Pz9gPz8oPxhFAhY/OT8/Pz8=")
                grabzIt.URLToImage("http://update.poke.one/notice")
                filepath = "./notice_online.jpg"
                grabzIt.SaveTo(filepath)
                im = Image.open('./notice_online.jpg')
                left = 0
                top = 0
                right = 1024
                bottom = 300
                im1 = im.crop((left, top, right, bottom)) 
                im1.save('./notice_online.png')
                os.remove("./notice_online.jpg")
                window["-image-"].update("./notice_online.png")
                
            except:
                sg.Popup('Something went wrong...', keep_on_top=True,title="Error")
            
        elif event == 'Launch' and updating == False:
            #if platform.system() == "Windows":
            #   os.system("start ./PokeOne.exe")
            if platform.system() == "Linux":
                #print("Linux needs wine-staging & dxvk")
                try:
                    os.system("wine ./PokeOne.exe")
                except:
                    sg.Popup('Something went wrong...', keep_on_top=True,title="Error")
            if os.path.exists("./PokeOne.exe") == False:
                sg.Popup('Can´t find Game executable... Is it correctly installed / updated?', keep_on_top=True,title="Error")
            else:
                print(platform.system + " is not Supported")
        elif event == 'Update':
            updating = True
            runUpdate(window=window)
            window["status"].update("Finished!")
            window['progress'].update_bar(100)
            updating = False
    window.close()


def runUpdate(timeout=None, window=None):

    parseUpdate(window)
    try:
        nop = None
        cmd = ""
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        for line in p.stdout:
            line = line.decode(errors='replace' if (sys.version_info) < (
                3, 5) else 'backslashreplace').rstrip()
            output += line

            window.refresh() if window else nop

        retval = p.wait(timeout)
        return (retval, output)
    except:
        pass


def parseUpdate(window=None):
    
    filesurl = 'http://update.poke.one/files'
    urllib.request.urlretrieve(filesurl, 'files')
    f = open('files')
    line = f.readline()
    while line:
        linePart = line.partition('>')[0].replace('\\', '/')
        window["status"].update("Downloading...")
        download(linePart, window)
        line = f.readline()
    window["status"].update("Extracting...")
    try:
        extractFile(window)
        f.close()
    except:
        pass


def download(file, window=None):
    downloadString = ("http://update.poke.one/request/" +
                      file).replace(" ", "%20")
    req = urllib.request.Request(downloadString, method='HEAD')
    r = urllib.request.urlopen(req)
    outputfile = downloadString.replace("http://update.poke.one/request/", "")
    print(outputfile)
    outputfile = outputfile + ".zip"

    num_lines = sum(1 for line in open('files'))
    global currentfile
    count = 0
    with open('files', 'r') as f:
        for line in f:
            count += 1
    currentfile += 1
    window["count"].update(str(currentfile) + " / " + str(count))
    window.refresh()
    f = requests.get(downloadString)
    try:
        f2 = open(outputfile, "wb").write(f.content)

    except:
        pass

    window['progress'].update_bar(currentfile / count * 100)
    window.refresh()


def extractFile(window=None):
    rootpath = pathlib.Path().absolute()
    print(rootpath)
    global currentfile
    count = 0
    with open('files', 'r') as f:
        for line in f:
            count += 1
    window['progress'].update_bar(0)
    for root, dirs, files in os.walk(rootpath):
        for name in files:
            if name.endswith((".zip", ".ZIP")):
                print("Extracting file from Archive: " +
                      str(os.path.join(root, name)))
                path = pathlib.Path(os.path.join(root, name))
                print(path.parent)
                os.chdir(path.parent)
                file_name = (name)  # get full path of files
                print(file_name)
                zip_ref = zipfile.ZipFile(path)  # create zipfile object
                zip_ref.extractall()  # extract file to dir
                zip_ref.close()  # close file
                os.remove(file_name)  # delete zipped file
                window.refresh()
                currentfile += 1
                window['progress'].update_bar(currentfile / count * 100)
    os.chdir(rootpath)


    # for root, dirs, files in os.walk("."):
    #	for name in files:
    #		if name.endswith((".zip", ".ZIP")):
    #			os.remove(name)
main()
