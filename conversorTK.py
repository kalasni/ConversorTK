# -*- coding: utf-8 -*-


####################################################
# CambiaFormatos 1.0: Programa gráfico que automatiza la conversión de archivos
# de audio de un formato a otro. 
# This program can convert audio files into mp3, wav, ogg and wma format.
# You need to have some programs installed such as, lame, mplayer, mpg123,
# ogg2mp3 and mp32ogg.
# 
# 
# 15-6-08 coded by Kalasni
# Tested on FreeBSD and Ubuntu Linux
#
#
# 1. Chose format you want to convert (mp3 to wav, wma to mp3, etc).
# 2. Go to "Dir" -> "Go to" and select the dir where the files are.
# 3. Press "OK" button and the process will start.
# 4. You can stop the process pressing "Stop" button.

####################################################

import glob
import commands
import os
import signal
import time
import threading
import tkFont
import tkFileDialog
from subprocess import *  # Para la class Popen
from Tkinter import *
from tkMessageBox import showerror, showinfo


""" Clase Hilo donde se ejecutan los procesos """
class Hilo(threading.Thread):
	
	# Pasamos como parametro la clase Conversor y la variable de los radioButtons
	def __init__(self, Conversor, radioVari):
		threading.Thread.__init__(self)
		self.conversor = Conversor
		self.formatoEle = radioVari
		
	def run(self):
		
		print "SELECTED FORMAT"
		print self.formatoEle
		
		time.sleep(1)
		formato = self.formatoEle
		if formato == 1:
			self.conversor.mp3_a_wav()
		elif formato == 2:
			self.conversor.wav_a_mp3()
		elif formato == 3:
			self.conversor.ogg_a_mp3()
		elif formato == 4:
			self.conversor.mp3_a_ogg()	
		elif formato == 5:
			self.conversor.wma_a_wav()
		elif formato == 6:
			self.conversor.wma_a_mp3()	
			
			
""" Clase principal donde se definen todos los metodos principales """				
class Conversor(Frame):
	
	def __init__(self, master):
        	Frame.__init__(self, master)
		
		self.labl = StringVar()
		self.radioVari = IntVar()
		self.pidNum = 0
		self.fonts = tkFont.Font(family="Helvetica", size=15, weight="normal")
		
		# Propiedades de la GUI
		self.master.wm_minsize(width='390', height='210')
		self.master.title("ConversorTK v1.0")
		self.master.protocol('WM_DELETE_WINDOW', root.quit())
        	self.pack(expand=YES, fill=BOTH)
        	self.createWidgets()
		
	""" 
	Mata el proceso de la shell creado mediante Popen.
	De momento la forma de localizar el numero de proceso creado es un poco
	ruda. Generalmente el numero de proceso es una unidad más que el id de
	proceso asignado cuando se ejecuta Popen. Así, si el id asignado al proceso 
	Popen es por ejemplo 1342, el id asignado al proceso llamado dentro de
	Popen es una unidad más, 1343. """				
	def stop(self):
		if self.pidNum == 0:
			dialog = showinfo('Select dir', 'You must select a dir.')
		else:	
			print "Kill process: "
			print self.pidNum
			try:
				os.kill(self.pidNum + 1, signal.SIGKILL)
			except Exception:
				print "Exception trying to kill process"
				print self.pidNum + 1
				self.pidNum = 0
		
				
	# Metodo donde se llama a la clase Hilo para que ejecute el método relativo
	# al formato que se le pasa como parámetro.
	def cambiar(self):
		
		formato = self.radioVari.get()
		try:
			directorio = self.direct  # self.direct se establece en devuelveDir()
			Hilo(self, formato).start()
		except AttributeError:
			dialog = showinfo('Select dir', 'You must select a dir.')
		
		
		
	# Muestra el askdirectory para seleccionar la carpeta de donde se van
	# a procesar los archivos.
	def devuelveDir(self):
				
		# Obtenemos el valor de la variable seleccionada en los radiobuttons
		# para poder añadir la extensión requerida.
		if self.radioVari.get() == 0:
			dialog = showinfo('Select Format', 'You must select a format.')
			return
		else:		
			ext = self.radioVari.get()
			if ext == 1 or ext == 4:
				exten = "mp3"
			elif ext == 2:
				exten = "wav"
			elif ext == 3:
				exten = "ogg"
			elif ext == 5 or ext == 6:
				exten = "wma"	
						
		carpeta = tkFileDialog.askdirectory(parent=root, initialdir="/home/",
				                   title='Select a dir')
						   				   				   
		if len(carpeta) < 1:
			dialog = showinfo('Select dir', 'You must select a dir.')
		elif len(carpeta) > 1:	
			self.direct = carpeta
			print "Into %s " % (self.direct)
			print " "
			print "Changing spaces and cleaning characters "
			print "....."
			print "..."
			os.chdir(self.direct)
			for i in glob.glob(self.direct + '/*.' + exten):
				
				# cambiamos espacios por guiones bajos _
				os.rename(i, self.stripnulls(i))
				time.sleep(0.5)
				
			# Eliminamos caracteres conflictivos y al final renombramos
			# el archivo
			for i in glob.glob(self.direct + '/*.' + exten):
				title = i
				if title.count("("):
					title = self.limpiaTitle("(", title)
				if title.count(")"):
					title = self.limpiaTitle(")", title)
				if title.count("'"):
					title = self.limpiaTitle("'", title)	
				if title.count("&"):
					title = self.limpiaTitle("&", title)			
				os.rename(i, title)												
			print "Done! "
				
				
	# Convierte de formato mp3 a wav		
	def mp3_a_wav(self):
		
		# De cada archivo añadido a la lista se extrae el nombre del mismo sin
		# la extensión y se transforma al formato elegido.
		for i in glob.glob(self.direct + '/*.mp3'):
			base, extension = os.path.splitext(i)
			comando ="mpg123 -w %s.wav %s" % (base, i)
			p = Popen(comando, shell=True)
			self.pidNum = p.pid
			print "PROCESS NUMBER: "
			print self.pidNum
			
			"""  La diferencia entre poll() y exit() es que el primero testea 
			 y sigue, mientras que el segundo espera a que acabe el proceso
			 y entonces devuelve returncode """
			
			# Mientras no termine el proceso muestra ESPERE
			while p.poll() == None:
				self.labl.set("    WAIT    ")
			self.labl.set("FINISHED")
			
				
	# Convierte de formato wav a formato mp3		
	def wav_a_mp3(self):
				
		for i in glob.glob(self.direct + '/*.wav'):
			base, extension = os.path.splitext(i)
			comando ="lame -b 192 %s %s.mp3" % (i, base)
			p = Popen(comando, shell=True)
			self.pidNum = p.pid
			print "PROCESS NUMBER: "
			print self.pidNum
			
			# Mientras no termine el proceso muestra ESPERE
			while p.poll() == None:
				self.labl.set("    WAIT    ")
			self.labl.set("FINISHED")
				
			
	# Convierte de formato ogg a mp3
	def ogg_a_mp3(self):
				
		comando = "ogg2mp3 --bitrate=192 -verbose %s" % (self.direct)
		p = Popen(comando, shell=True)
		self.pidNum = p.pid
		print "PROCESS NUMBER: "
		print self.pidNum
		while p.poll() == None:
			self.labl.set("    WAIT    ")
		self.labl.set("FINISHED")		
								
								
	# Convierte de formato mp3 a ogg
	def mp3_a_ogg(self):
			
		comando = "mp32ogg --verbose %s" % (self.direct)
		p = Popen(comando, shell=True)
		self.pidNum = p.pid
		print "PROCESS NUMBER: "
		print self.pidNum
		while p.poll() == None:
			self.labl.set("    WAIT    ")
		self.labl.set("FINISHED")	
		
		
	# Convierte de formato Wma a wav
	def wma_a_wav(self):
			
		for i in glob.glob(self.direct + '/*.wma'):
			base, extension = os.path.splitext(i)
			comando = "mplayer -vo null -vc dummy -af resample=44100 -ao pcm:file=%s.wav %s" % (base, i)
			p = Popen(comando, shell=True)
			self.pidNum = p.pid
			print "PROCESS NUMBER: "
			print self.pidNum
			
			# Mientras no termine el proceso muestra ESPERE
			while p.poll() == None:
				self.labl.set("    WAIT    ")
			self.labl.set("FINISHED")
				
								
	# Convertir de wma a mp3
	def wma_a_mp3(self):
		
		# Primero convierte de wma a wav
		for i in glob.glob(self.direct + '/*.wma'):
			base, extension = os.path.splitext(i)
			comando = "mplayer -vo null -vc dummy -af resample=44100 -ao pcm:file=%s.wav %s" % (base, i)
			
			p = Popen(comando, shell=True)
			self.pidNum = p.pid
			print "PID PROCESS NUMBER: "
			print self.pidNum
			while p.poll() == None:
				self.labl.set("    WAIT    ")
							
			# Una vez están todos en formato wav se pasan a mp3				
			for i in glob.glob(self.direct + '/*.wav'):
				base, extension = os.path.splitext(i)
				comando2 = "lame -b 192 %s %s.mp3" % (i, base)
				p = Popen(comando2, shell=True)
				self.pidNum = p.pid
				print "PID PROCESS NUMBER: "
				print self.pidNum
				while p.poll() == None:
					pass
				#os.system("rm *.wav")
			self.labl.set("FINISHED")
			
							
	# Elimina los espacios al principio y al final y sustituye los espacios entre palabras
	# por guiones bajos.						
	def stripnulls(self, datos):
		return datos.replace(" ", "_").strip()
		
	# Elimina el caracter que pasemos como parametro
	def limpiaTitle(self, car, datos):
		return datos.replace(car, "")	
						
	# Borra la etiqueta cada vez que se activa un radioButton diferente.				
	def borraLabel(self):
		self.labl.set("                        ") # 24 esp
		
	# Muestra dialogo de ayuda
	def ayuda(self):
		showinfo(
			" About ",
			"\nConversorTK v1.0 \nCoder: Kalasni\n"
			"Contact: kalassni@gmail.com\n",		
		)	
			
					
	def check(self):
		
		lame = commands.getstatusoutput("type lame")
		if lame[0] == 0:
			pass
		elif lame[0] != 0:
			print "You need to install lame program"
			
		mpg123 = commands.getstatusoutput("type mpg123")
		if mpg123[0] == 0:
			pass
		elif mpg123[0] != 0:
			print "You need to install mpg123 program"
			
		mp32ogg = commands.getstatusoutput("type mp32ogg")
		if mp32ogg[0] == 0:
			pass
		elif mp32ogg[0] != 0:
			print "You need to install mp32ogg program"
			
		mplayer = commands.getstatusoutput("type mplayer")
		if mplayer[0] == 0:
			pass
		elif mplayer[0] != 0:
			print "You need to install mplayer program"
		
		ogg2mp3 = commands.getstatusoutput("type ogg2mp3")
		if ogg2mp3[0] == 0:
			pass
		elif ogg2mp3[0] != 0:
			print "You need to install ogg2mp3 program"
		
		"""noexiste = commands.getstatusoutput("type noexiste")
		if noexiste[0] == 0:
			pass
		elif noexiste[0] != 0:	
			print "Tienes que instalar el programa noexiste"""
			
					
	# Creamos todos los widgets				
	def createWidgets(self):
		
		self.labl.set("                        ") # 24 esp
		menub = Menu(self, font=self.fonts)
		filemenu = Menu(menub, font=self.fonts, tearoff=0)
		filemenu2 = Menu(menub, font=self.fonts, tearoff=0)
		filemenu.add_command(label="Go to", command=self.devuelveDir)
		filemenu.add_command(label="Exit", command=root.quit)
		filemenu2.add_command(label="About", command=self.ayuda)
		filemenu2.add_command(label="Check", command=self.check)
		menub.add_cascade(label="Dir", menu=filemenu)
		menub.add_cascade(label="Help", menu=filemenu2)
		root.config(menu=menub)
			
		marco1 = Frame(self, borderwidth=2, relief=GROOVE)
		Radiobutton(marco1, text="mp3 to Wav", font=self.fonts, variable=self.radioVari, value=1, command=self.borraLabel).pack(anchor=NW)
		Radiobutton(marco1, text="Wav to mp3", font=self.fonts, variable=self.radioVari,
	        value=2, command=self.borraLabel).pack(anchor=NW)
		Radiobutton(marco1, text="Ogg to mp3",font=self.fonts, variable=self.radioVari,
	        value=3, command=self.borraLabel).pack(anchor=NW)
		marco1.grid(row=1, column=1, padx=5, pady=10, sticky=N+W)
		
		marco2 = Frame(self, borderwidth=2, relief=GROOVE)
		Radiobutton(marco2, text="mp3 to Ogg", font=self.fonts, variable=self.radioVari, value=4, command=self.borraLabel).pack(anchor=NW)
		Radiobutton(marco2, text="Wma to Wav", font=self.fonts, variable=self.radioVari,
	        value=5, command=self.borraLabel).pack(anchor=NW)
		Radiobutton(marco2, text="Wma to mp3", font=self.fonts, variable=self.radioVari, value=6, command=self.borraLabel).pack(anchor=NW)
		marco2.grid(row=1, column=2, padx=5, pady=10, sticky=N+W)
		
		marco3 = Frame(self,borderwidth=2, relief=FLAT)
		Button(marco3, text='OK',  highlightthickness=2, activebackground='#90EE90', font=self.fonts, command=self.cambiar).grid(row=2, column=2, padx=12, pady=10)
		
		Label(marco3, text='', relief=GROOVE, font=self.fonts, foreground='#B51032', textvariable=self.labl, takefocus=1).grid(row=2, column=4, padx=12, pady=10)
		
		Button(marco3, text='STOP', highlightthickness=2 ,activebackground='#90EE90', font=self.fonts, command=self.stop).grid(row=2, column=6, padx=12, pady=10)
		marco3.grid(row=2, column=1, columnspan=4)
		
		marco4 = Frame(self, background='#DDDDDD')
		marco4.grid(row=3, pady=10)
		
		self.columnconfigure(1, weight=1)
	        self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
						
						
if __name__ == '__main__':
	
	root = Tk()
	app = Conversor(master=root)
	app.mainloop()
