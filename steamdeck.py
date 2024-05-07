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




import requests
import wget
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtsignal as Signal
from PyQt5.QtWidgets import (
	QApplication,
	QPushButton,
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QProgressBar,
	QMessageBox,
	QCheckBox,
)
from tqdm.auto import tqdm
import shlex

#sys.stdout = open(os.devnull, "w")
#sys.stderr = open(os.devnull, "w")

processing = False
only_update = False
new_install = True
updatefiles = 0
autolaunch = False
install_directory = os.path.expanduser( '~' ) + "/PokeOne/"
print(install_directory)

class downloadNewThread(QThread):
	data_downloaded = Signal(object)
	perc_downloaded = Signal(object)
	current_link = Signal(object)

	def __init__(self):
		QThread.__init__(self)

	#def __del__(self):
	#	try:
	#		subprocess.Popen("gamedata/PokeOne.exe")
	#	except Exception as e:
	#		print(e)
#
#		pass

	def run(self):
		try:
			try:
				os.remove(install_directory + "sys/update")
			except:
				pass
			with open(install_directory + "sys/defaultfiles") as f1:
				f1_text = f1.readlines()
			with open(install_directory + "sys/files") as f2:
				f2_text = f2.readlines()
			update_file = open(install_directory + "sys/update", "w")
			f2.close()

			# Find and print the diff:
			for line in difflib.unified_diff(f1_text, f2_text):
				if line[0] == "+" and line[1] != "+":
					#print(line)
					n = update_file.write(line)
			update_file.close()
		except:
			e = sys.exc_info()[0]
			#msg = QMessageBox()
			#msg.setText(str(e))
			print(e)
		filearray = []
		f = open(install_directory + "sys/update")
		line = f.readline()
		while line:
			linePart = line.partition(">")[0].replace("\\", "/").replace("+", "")
			# window["status"].update("Downloading...")
			filearray.append(linePart)
			line = f.readline()
		for item in filearray:
			#print(filearray.index(item))
			self.current_link.emit(item)
			download(item, self.perc_downloaded)
			self.data_downloaded.emit(filearray.index(item) * 73 / 100)
		filesurl = "http://update.poke.one/files"
		urllib.request.urlretrieve(filesurl,install_directory +  "sys/defaultfiles")
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
			os.remove(install_directory + "sys/files")
		except Exception as e:
			print(e)
		if error == False:
			urllib.request.urlretrieve(filesurl, install_directory + "sys/files")
			f = open(install_directory + "sys/files")
			line = f.readline()
			while line:
				linePart = line.partition(">")[0].replace("\\", "/")
				# window["status"].update("Downloading...")
				filearray.append(linePart)
				line = f.readline()
			for item in filearray:
				#print(filearray.index(item))
				self.current_link.emit(item)
				download(item, self.perc_downloaded)
				self.data_downloaded.emit(filearray.index(item))
			try:
				os.remove(install_directory + "sys/defaultfiles")
			except:
				pass
			shutil.copyfile(install_directory + "sys/files",install_directory +  "sys/defaultfiles")
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
		#print(rootpath)
		global currentfile
		count = 0
		# error check
		try:
			with open(install_directory + "sys/files", "r") as f:
				pass
		except Exception as e:
			print(e)
			
		if error == False:
			if only_update == False:
				with open(install_directory + "sys/files", "r") as f:
					for line in f:
						count += 1
			else:
				with open(install_directory + "sys/update", "r") as f:
					for line in f:
						count += 1
			try:
				#print(currentfile)
				try:
					for root, dirs, files in os.walk(install_directory):
						for name in files:
							if name.endswith((".zip", ".ZIP")):
								print(
									"Extracting file from Archive: "
									+ str(os.path.join(root, name))
								)
								path = pathlib.Path(os.path.join(root, name))
								#print(path.parent)
								os.chdir(path.parent)
								file_name = name  # get full path of files
								#print(file_name)
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
					os.chdir(install_directory)
				except Exception as e:
					print(e)
					os.chdir(install_directory)
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
		if path.exists(install_directory + "sys/installed"):
			print("not a new install")
			new_install = False
		else:
			print("is a new install")
			new_install = True
		
		open(install_directory + "sys/installed", "a").close()
		if new_install == True:
			self.goself()
		else:
			if path.exists(install_directory + "sys/updating"):
				print("error while donwloading")
				try:
					os.remove(install_directory + "sys/updating")
				except:
					pass
				self.goself()
			else:
				self.checknew()
	def import_all(self):
		pass

	def goself(self):
		autolaunch = False
		self.autocheckbox.setEnabled(False)
		try:
			os.remove(install_directory + "sys/files")
		except:
			pass
		open(install_directory + "sys/updating", "a").close()
		self.btn_go.setEnabled(False)
		#self.btn_r.setEnabled(False)
		#self.btn_c.setEnabled(False)
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
		#self.btn_c.setEnabled(False)
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
	def disable_Buttons(self):
		self.btn_go.setEnabled(False)
		self.btn_launch.setEnabled(False)
		
	def on_finished_ex(self):
		self.btn_go.setEnabled(True)
		# self.btn_x.setEnabled(True)
		#self.btn_c.setEnabled(True)
		#self.btn_r.setEnabled(True)
		self.btn_launch.setEnabled(True)
		self.progressfile.setValue(100)
		self.progressall.setValue(73)
		self.label_curr.setText("Finished!")
		self.autocheckbox.setEnabled(True)
		try:
			os.remove(install_directory + "sys/updating")
		except:
			pass
	def on_data_ready(self, data):
		#print(data)
		self.progressall.setValue(data)

	def updateperc(self, data):
		#print(data)
		self.progressfile.setValue(data)

	def updateLabel(self, data):
		self.label_curr.setText(data)

	def launchGame(self):
		if os.name == 'nt':
			try:
				subprocess.Popen(install_directory + "gamedata/PokeOne.exe")
			except Exception as e:
				print(e)
		else:
			try:
				subprocess.Popen("flatpak run --command=bottles-cli com.usebottles.bottles run -b P1 -e" + install_directory + "gamedata/PokeOne.exe", shell=True)

			except Exception as e:
				print(e)
				try:
					subprocess.Popen("bottles run -b P1 -e" + install_directory + "gamedata/PokeOne.exe", shell=True)

				except Exception as e:

					print(e)
	def letmeout(self):
		self.close()
	def setup(self):

		vbox = QVBoxLayout(self)
		self.btn_go = QPushButton("Full Download", self)
		self.btn_go.clicked.connect(self.goself)
		self.btn_go.resize(80, 20)
		self.btn_go.move(700 - 66 - 80, 0 + 2)
		self.QHBoxLayoutLaunch = QHBoxLayout()
		self.autocheckbox = QCheckBox("Automatic Launch (After Next Start ~4s)", self)
		self.autocheckbox.resize(40,90)
		self.autocheckbox.stateChanged.connect(self.update_checkbox_state)
		
		
		self.btn_launch = QPushButton("Launch", self)
		self.btn_launch.clicked.connect(self.launchGame)
		self.btn_launch.setFixedSize(404, 120)
		self.btn_launch.move(13, 315)
		self.btn_launch.setStyleSheet("background-color : orange")
		self.label_curr = QLabel("")
		self.label_progress = QLabel("Progress:")
		self.progressfile = QProgressBar(self)
		self.progressfile.setGeometry(0, 0, 300, 25)
		self.progressfile.setMaximum(100)
		self.progressall = QProgressBar(self)
		self.progressall.setGeometry(0, 0, 300, 25)
		self.progressall.setMaximum(73)
		self.Spacer = QtWidgets.QSpacerItem(20, 20)
		self.btn_exit = QPushButton("Exit", self)
		self.btn_exit.clicked.connect(self.letmeout)
		vbox.addItem(self.Spacer)

		vbox.addWidget(self.label_curr)
		vbox.addWidget(self.progressfile)
		vbox.addWidget(self.label_progress)
		vbox.addWidget(self.progressall)
		vbox.addWidget(self.btn_go)
		self.QHBoxLayoutLaunch.addStretch(1)
		self.QHBoxLayoutLaunch.addWidget(self.btn_launch,stretch=3)
		self.QHBoxLayoutLaunch.addWidget(self.autocheckbox)
		vbox.addLayout(self.QHBoxLayoutLaunch)
		vbox.addWidget(self.btn_exit)
		self.setLayout(vbox)
		self.setGeometry(100, 100, 200, 150)
		self.setFixedSize(700, 320)
		self.setWindowTitle("PokeOne Launcher SteamDeck Edition")
		vbox.setAlignment(QtCore.Qt.AlignCenter)
		if path.exists(install_directory + "sys/autolaunch"):
			autolaunch = True
			self.btn_go.setEnabled(False)
			self.btn_launch.setEnabled(False)
		else:
			autolaunch = False
		if autolaunch == True:
			self.disable_Buttons()
			self.autocheckbox.setChecked(True)
			self.autotimer = QtCore.QTimer(self)
			self.autotimer.timeout.connect(self.launchGame)
			self.autotimer.setSingleShot(True)
			self.autotimer.start(4000)
		else:
			self.btn_go.setEnabled(True)
			self.btn_launch.setEnabled(True)
	def update_checkbox_state(self):
		if self.autocheckbox.isChecked():
			open(install_directory + "sys/autolaunch", "a").close()
		else:
			os.remove(install_directory + "sys/autolaunch")
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
		urllib.request.urlretrieve(filesurl,install_directory + "sys/files")
		f = open(install_directory + "sys/files")
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
		urllib.request.urlretrieve(filesurl,install_directory + "sys/files")
		f = open(install_directory + "sys/update")
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





def download(file, percobj):
	downloadString = ("http://update.poke.one/request/" + file).replace(" ", "%20")
	try:
		req = urllib.request.Request(downloadString, method="HEAD")
		r = urllib.request.urlopen(req)
		outputfile = downloadString.replace("http://update.poke.one/request/", "")
		outputfile = install_directory + "gamedata/" + outputfile + ".zip"
		#print(outputfile)
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
		#msg = QMessageBox()
		#msg.setText(str(e))
		print(e)


def checkupdates():
	import difflib

	print("running check")
	try:
		try:
			os.remove(install_directory + "sys/update")
		except:
			pass
		with open(install_directory + "sys/defaultfiles") as f1:
			f1_text = f1.readlines()
		with open(install_directory + "sys/files") as f2:
			f2_text = f2.readlines()
		update_file = open(install_directory + "sys/update", "w")
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
		msg.exec()





def createFiles():
	try:
		os.makedirs(install_directory)
		if path.exists(install_directory + "gamedata/") == False:
			os.mkdir(install_directory + "gamedata/")
		os.makedirs(install_directory + "gamedata/PokeOne_Data/StreamingAssets/", exist_ok=True)
		os.makedirs(install_directory + "gamedata/PokeOne_Data/Resources/", exist_ok=True)
		os.makedirs(install_directory + "gamedata/PokeOne_Data/Plugins/", exist_ok=True)
		os.makedirs(install_directory + "gamedata/PokeOne_Data/il2cpp_data/Resources/", exist_ok=True)
		os.makedirs(install_directory + "gamedata/PokeOne_Data/il2cpp_data/Metadata/", exist_ok=True)
		os.makedirs(
			install_directory + "gamedata/PokeOne_Data/il2cpp_data/etc/mono/mconfig/", exist_ok=True
		)
		os.makedirs(
			install_directory + "gamedata/PokeOne_Data/il2cpp_data/etc/mono/4.5/Browsers/", exist_ok=True
		)
		os.makedirs(
			install_directory + "gamedata/PokeOne_Data/il2cpp_data/etc/mono/4.0/Browsers/", exist_ok=True
		)
		os.makedirs(
			install_directory + "gamedata/PokeOne_Data/il2cpp_data/etc/mono/2.0/Browsers/", exist_ok=True
		)

		if path.exists(install_directory + "sys/") == False:
			os.mkdir(install_directory + "sys/")

		if path.exists(install_directory + "sys/defaultfiles") == False:
			wget.download("http://update.poke.one/files", out=install_directory + "sys/defaultfiles")
		if path.exists(install_directory + "sys/files") == False:
			wget.download("http://update.poke.one/files", out=install_directory + "sys/files")

	except:
		pass
	# wget.download("http://update.poke.one/notice",out="sys/notice.html")
app = QApplication(sys.argv)
# app.setStyleSheet(qdarkstyle.load_stylesheet())
tqdm.monitor_interval = 0
launchWin = Launcher()

sys.exit(app.exec())

if __name__ == "__main__":
	# with open('errorlog.txt', 'w') as out:
	#    with redirect_stdout(out):
	#     run()#
	run()
