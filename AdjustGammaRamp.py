#!/usr/bin/python
# thanks to Martin Spacek in http://www.mail-archive.com/pyglet-users@googlegroups.com/msg00608.html

import pyglet.window
import numpy as np
from ctypes import windll
import sys 
import time 
import os.path

def main(argv):
	GammaRampFileName = 'GammaRamp.npy'
	action = ''
	Usage = False

	if len(sys.argv) > 1: 
		action = sys.argv[1]

	if action == 'Save': 
		if len(sys.argv) > 2: 
			GammaRampFileName = sys.argv[2]
		
		win = pyglet.window.Window( visible=False)

		OrigRamps = np.empty((3, 256), dtype=np.uint16) # init R, G, and B ramps

		# try and get gamma ramp
		success = windll.gdi32.GetDeviceGammaRamp(win._dc, OrigRamps.ctypes)
		if not success: raise AssertionError, 'GetDeviceGammaRamp failed'

		# Save Gamma Ramp
		np.save(GammaRampFileName, OrigRamps)
		print 'Gamma ramp saved' 
	elif action == 'Restore': 
		if len(sys.argv) > 2: 
			GammaRampFileName = sys.argv[2]
		win = pyglet.window.Window( visible=False)

		OrigRamps = np.load(GammaRampFileName)
		if OrigRamps.size == 0: raise AssertionError, 'Loading of Gamma Ramp file failed'

		# reset to original gamma
		success = windll.gdi32.SetDeviceGammaRamp(win._dc, OrigRamps.ctypes)
		if not success: raise AssertionError, 'SetDeviceGammaRamp failed'
		print 'Gamma ramp restored'
	elif action == 'Adjust':
		if len(sys.argv) < 5: 
			Usage = True
		else: 
			
			if len(sys.argv) > 5: 
				GammaRampFileName = sys.argv[5]

			Scale = np.array( [ [sys.argv[2]], [sys.argv[3]], [sys.argv[4]] ], float )
			#print Scale
		
			win = pyglet.window.Window( visible=False)

			# Check if gamma ramp was saved
			if os.path.isfile(GammaRampFileName) : 
				OrigRamps = np.load(GammaRampFileName)
				if OrigRamps.size == 0: raise AssertionError, 'Loading of Gamma Ramp file failed'
			else : 
				# Save current gamma ramp
				OrigRamps = np.empty((3, 256), dtype=np.uint16) # init R, G, and B ramps

				# try and get gamma ramp
				success = windll.gdi32.GetDeviceGammaRamp(win._dc, OrigRamps.ctypes)
				if not success: raise AssertionError, 'GetDeviceGammaRamp failed'

				# Save Gamma Ramp
				np.save(GammaRampFileName, OrigRamps)

			NewRamps = np.uint16(np.round(np.multiply(Scale, OrigRamps)))

			# try and set gamma ramp
			success = windll.gdi32.SetDeviceGammaRamp(win._dc, NewRamps.ctypes)
			if not success: raise AssertionError, 'SetDeviceGammaRamp failed'

			print 'Gamma ramps adjusted' 
	elif action == 'Slide':
		if len(sys.argv) < 10: 
			Usage = True
		else : 

			if len(sys.argv) > 10: 
				GammaRampFileName = sys.argv[10]

			StartScale = np.array( [ [sys.argv[2]], [sys.argv[3]], [sys.argv[4]] ], float )
			EndScale = np.array( [ [sys.argv[7]], [sys.argv[8]], [sys.argv[9]] ], float )
			Steps = int(sys.argv[5])
			StepDelay = int(sys.argv[6])

			win = pyglet.window.Window( visible=False)

			# Check if gamma ramp was saved
			if os.path.isfile(GammaRampFileName) : 
				# Load saved gamma ramp
				OrigRamps = np.load(GammaRampFileName)
				if OrigRamps.size == 0: raise AssertionError, 'Loading of Gamma Ramp file failed'
			else : 
				# Save current gamma ramp
				OrigRamps = np.empty((3, 256), dtype=np.uint16) # init R, G, and B ramps

				# try and get gamma ramp
				success = windll.gdi32.GetDeviceGammaRamp(win._dc, OrigRamps.ctypes)
				if not success: raise AssertionError, 'GetDeviceGammaRamp failed'

				# Save Gamma Ramp
				np.save(GammaRampFileName, OrigRamps)

			for ScaleX in range(0, (Steps+2)):
				CrrntScaleX = float(ScaleX)/(Steps+1)
				
				CrrntScale = np.multiply(StartScale, ( 1- CrrntScaleX)) + np.multiply(EndScale, CrrntScaleX )
				#print ScaleX , float(ScaleX)/(Steps+1), CrrntScale 
				
				NewRamps = np.uint16(np.round(np.multiply(CrrntScale, OrigRamps)))

				# try and set gamma ramp
				success = windll.gdi32.SetDeviceGammaRamp(win._dc, NewRamps.ctypes)
				if not success: raise AssertionError, 'SetDeviceGammaRamp failed'

				if ScaleX < Steps+1 : 
					time.sleep(StepDelay)
			
	else :
		Usage = True
		
	if Usage : 
		print 'Usage: ' 
		print '  Save [File name]          : Saves current gamma ramp'
		print '  Restore [File name]       : Restores saved gamma ramp'
		print '  Adjust R G B [File name]  : Adjust gamma ramp, uses saved gamma ramp as source. Saves gamma ramp if file not found.' 
		print '  Slide Start_R Start_G Start_B Steps StepDelay End_R End_G End_b [File name] : Do a slow slide between StartRGB and EndRGB, with number of Steps, with StepDelay in seconds between steps. Saves gamma ramp if file not found.'
		print 'Examples:'
		print '  Change to night time: ', sys.argv[0], ' Slide 1 1  1  40 1 1 .8 .8 '
		print '  Change to day time  : ', sys.argv[0], ' Slide 1 .8 .8 40 1 1 1  1 '

if __name__ == "__main__":
   main(sys.argv[1:])