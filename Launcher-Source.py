import os
import subprocess
import sys
import urllib.request
import zipfile
import threading
from zipfile import ZipFile
import time
import pathlib
import PySimpleGUI as sg
import requests
from tqdm.auto import tqdm
import wget
import platform
import filecmp

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.devnull, "w")
tqdm.monitor_interval = 0

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

print(resource_path(os.getcwd()))


sg.theme('DarkTanBlue')
currentfile = 0
options = {
    'format': 'png',
    'crop-h': '500',
    'encoding': "UTF-8",
}

filearray = []
thread_finished = threading.Event()
result_available = threading.Event()

def download_thread(arg1, window):
    for item in arg1:
        print(item)
        download(item,window) 
        #window['p_t'].update_bar(0)  
        pass
    thread_finished.set()
    
def update_thread(window):
    window["Launch"].Update(disabled=True)
    window["Update"].Update(disabled=True)
    window["Exit"].Update(disabled=True)
    runUpdate(window=window)

    result_available.wait()
    extractFile(window)
    window["status"].update("Finished!")
    window['progress'].update_bar(100)
    updating = False
    window["Launch"].Update(disabled=False)
    window["Update"].Update(disabled=False)
    window["Exit"].Update(disabled=False)
def firefox_thread(opens,window):
    if opens == True:
        window["Exit"].Update(disabled=True)
        if platform.system() == "Linux":
            options = Options()
            options.binary_location = resource_path(os.getcwd()) + "/utils/firefox/firefox"
            options.add_argument("--headless") 
            driver = webdriver.Firefox(executable_path=(resource_path(os.getcwd()) + '/utils/firefox/geckodriver'),options=options)
            driver.get('http://update.poke.one/notice')
            driver.save_screenshot("./notice_online.png")
            driver.close()
            driver.quit()
        else:
            options = Options()
            options.binary_location = resource_path(os.getcwd()) + "/utils/firefox_win/firefox.exe"
            options.add_argument("--headless") 
            driver = webdriver.Firefox(executable_path=(resource_path(os.getcwd()) + '/utils/firefox_win/geckodriver.exe'),options=options)
            driver.get('http://update.poke.one/notice')
            driver.save_screenshot("./notice_online.png")
            driver.close()
            driver.quit()
        im = Image.open('./notice_online.png')
        left = 0
        top = 0
        right = 1024
        bottom = 500
        im1 = im.crop((left, top, right, bottom)) 
        im1.save('./notice_online.png')
        window["-image-"].update("./notice_online.png")
        window["Exit"].Update(disabled=False)
def main():

    if os.path.exists("./PokeOne_Data/") == False:
        sg.Popup('No data Folder found. Please extract all Files form your downloaded Archive!', keep_on_top=True,title="Error")
        window.close()
    layout = [
        [sg.Image("./notice.png",key="-image-",background_color="#000")],

    [sg.ProgressBar(max_value=100, orientation='h', size=(70, 20), key='p_t'), sg.Text(text="", key="perc", size=(8, 1))],
        [sg.ProgressBar(max_value=100, orientation='h', size=(70, 20), key='progress'), sg.Text(text="", key="totalfiles", size=(3, 1)), sg.Text(text="", key="count", size=(8, 1))],
        [sg.Button("Launch",size=(20,1)), sg.Button('Update',size=(20,1)), sg.Button('Exit',size=(20,1)), sg.Text(text="", key="status", size=(16, 1))]]
    window = sg.Window('PokeOne Updater - written in Python3',layout,resizable=False, finalize=True,disable_close=True)
    updating = False
    
    ft = threading.Thread(target=firefox_thread, args=(True,window,), daemon=True)
    ft.start()
    while True:
        event, values = window.read(timeout=40)
        if event in (sg.WIN_CLOSED, 'Exit'):
            ft = threading.Thread(target=firefox_thread, args=(False,window,), daemon=True)
            ft.start()
            break
        elif event == 'Launch' and updating == False:
            if platform.system() == "Windows":
               os.system("start ./PokeOne.exe")
            if platform.system() == "Linux":
                #print("Linux needs wine-staging & dxvk")
                try:
                    os.system("wine ./PokeOne.exe")
                except:
                    sg.Popup('Something went wrong...', keep_on_top=True,title="Error")
            elif os.path.exists("./PokeOne.exe") == False:
                sg.Popup('Can´t find Game executable... Is it correctly installed / updated?', keep_on_top=True,title="Error")
            else:
                print(platform.system + " is not Supported")
        elif event == 'Update':
            updating = True
            t2 = threading.Thread(target=update_thread, args=(window,), daemon=True)
            t2.start()
            updating = False
    window.close()


def runUpdate(timeout=40, window=None):

    parseUpdate(window)
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
    result_available.set()
    return (retval, output)
    

def parseUpdate(window=None):
    
    filesurl = 'http://update.poke.one/files'
    urllib.request.urlretrieve(filesurl, 'files')
    f = open('files')
    line = f.readline()
    while line:
        linePart = line.partition('>')[0].replace('\\', '/')
        window["status"].update("Downloading...")
        filearray.append(linePart)
        line = f.readline()
    t = threading.Thread(target=download_thread, args=(filearray, window,), daemon=True)
    t.start()
    thread_finished.wait()

def download(file, window=None):
    downloadString = ("http://update.poke.one/request/" +
                      file).replace(" ", "%20")
    req = urllib.request.Request(downloadString, method='HEAD')
    r = urllib.request.urlopen(req)
    outputfile = downloadString.replace("http://update.poke.one/request/", "")
    
    outputfile = outputfile + ".zip"
    print(outputfile)
    num_lines = sum(1 for line in open('files'))
    global currentfile
    count = 0
    
    with open('files', 'r') as f:
        for line in f:
            count += 1
    currentfile += 1
    window["count"].update(str(currentfile) + " / " + str(count))
    window.refresh()  
    response = requests.get(downloadString, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 32*1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(outputfile, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            window['p_t'].update_bar(round(progress_bar.n/total_size_in_bytes*100))
            window['perc'].update(round(progress_bar.n/total_size_in_bytes*100))
            window.refresh()
            file.write(data)
            
            window.refresh()
    #f2 = open(outputfile, "wb").write(response.content)
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
    window.refresh()
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
                window.refresh()
    os.chdir(rootpath)


    # for root, dirs, files in os.walk("."):
    #	for name in files:
    #		if name.endswith((".zip", ".ZIP")):
    #			os.remove(name)
main()

