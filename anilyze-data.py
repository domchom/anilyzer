# @File(label = "Input directory", style = "directory") experimentFolder
# @File(label = "Output directory", style = "directory") saveFolder

"""
##AUTHOR: Ani Michaud (Varjabedian)

## DESCRIPTION: This branch is a stripped down version of the anilyzer. All it does is open hyperstacks, max project everything, and saves the max projection in an output folder.

The organization of this code is as follows:

1. Script parameters (at the top, preceded by a "#@") that gather information for the dialogue box
2. Import statements for all the modules needed
3. All of the main functions for processing data
4. The run_it() function, which sets up the error logging, and then calls all of the other processing functions. It should eventually just be in it's own file, but I like having everything where you can see it.

If you want to know the general flow of events, check the order of calls in the run_it() function. If you want to skip certain steps, comment them out in the run_it() function. Although, be aware that some functions pass arguments to each other, and commenting out certain functions can result in errors. It's best to read the particular function before you comment it out to make sure you avoid this.

For more information and up-to-date changes, visit the GitHub repository: https://github.com/anivarj/anilyzer

"""

# Importing modules and other shit
import os, sys, traceback, shutil, glob
from ij import IJ, WindowManager, ImagePlus
from ij.gui import GenericDialog
from ij.plugin import ImageCalculator
import datetime
import fnmatch

experimentFolder = str(experimentFolder) # Converts the input directory you chose to a path string that can be used later on

saveFolder = str(saveFolder)

# Microscope_check assesses the file structure of the experimentFolder and assigns a "microscope type" which gets passed to other functions. This helps with determining where certain files and directories should be located.
def microscope_check(experimentFolder):
	#If it finds .oif files inside the main folder, it calls the microscope "Olympus"
	if any(File.endswith(".oif") for File in os.listdir(experimentFolder)):
		print(".oif files present, running Olympus pipeline")
		microscopeType = "Olympus"
		return microscopeType #returns microscopeType to run_it()
	else:
		#If there are no .oif files in the main folder, it calls the microscope "Bruker"
		print("No .oif files present, running Bruker pipeline")
		microscopeType = "Bruker"
		return microscopeType #returns microscopeType to run_it()

# list_scans gets a list of all scan folders inside the experimentFolder you selected, and saves them as a list called scanList.
def list_scans(experimentFolder, microscopeType):
	scanList = [] # Makes an empty list

	# This section screens out text files and other things that might be in the main experimentFolder, and only makes a list of the actual scan directories
	# For Bruker microscopes, the scan directories are plain, so os.isdir is used to look for them
	if microscopeType == "Bruker":
		for File in sorted(os.listdir(experimentFolder)):
			dirpath = os.path.join(experimentFolder, File) # Makes a complete path to the file
			if os.path.isdir(dirpath): # If the dirpath is a directory, print it and add it to scanList. If it's a file, do not add it.
				print "dirpath is " + dirpath
				scanList.append(dirpath)
		return scanList # Returns scanList to run_it()

	# If the microscope is "Olympus" type, the directories end in .oif.files, so .endswith needs to be used to find them
	if microscopeType == "Olympus":
		oifList = [] # This doesn't look like it was used, so I should delete it in the future once I have verified this.
		for File in sorted(os.listdir(experimentFolder)):
			if File.endswith(".oif.files"): # If the item ends with .oif.files, make the complete path and append it to scanList
				dirpath = os.path.join(experimentFolder, File)
				print "dirpath is " + dirpath
				scanList.append(dirpath)
		return scanList # Returns scanList to run_it()

# Make_hyperstack uses Bio-formats importer to import a hyperstack from an initiator file
def make_hyperstack(basename, scan, microscopeType): # basename is defined in run_it() and is the name of the scan (not the full path)

	# Defines an "initator file" to give bioformats importer, and also modifies basename (which has an .oif.files extension) to make the scan name
	if microscopeType == "Olympus":
		initiatorFileName = os.path.splitext(basename) [0] # Removes .file extension from the .oif.file path to get the name of the .oif initiator file
		basename = os.path.splitext(initiatorFileName) [0] # Removes .oif extension from initiatorFile to get the name of the scan (for naming windows and stuff)
		print "basename is ", basename
		print ".oif file is ",  initiatorFileName # This is the file that will get passed to bioformats importer
		initiatorFilePath = os.path.join(experimentFolder, initiatorFileName) # Gets the full path to the initiatorFile
		print "Opening file ", initiatorFilePath

	elif microscopeType == "Bruker": # With Bruker microscopes, you can initiate from the .xml file, or from a single TIF. I have found that initiation from the .xml file slows down the import on windows computers
		print "basename is ", basename # The basename doesn't need to be modified here, because there is no .oif.files suffix to remove (Thanks Bruker!)
		initiatorFileName = basename + "_Cycle00001_Ch?_000001.ome.tif" # Defines the pattern to look for. The Ch? is because if you have one color, it's not always on CH1
		initiatorFilePath = os.path.join(scan, initiatorFileName) # Gets the full path to the initiator file
		print "initiatorFilePath ", initiatorFilePath
		initiatorFilePath = glob.glob(initiatorFilePath) # Looks for the first file in the folder. If there are more than one channel, it makes a list of them.
		initiatorFilePath = initiatorFilePath[0] # Takes the first item in the list. This is the file that will get passed to bioformats importer
		print "Opening file", initiatorFilePath

	IJ.run("Bio-Formats Importer", "open=[" + initiatorFilePath + "] color_mode=Grayscale concatenate_series open_all_series quiet rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT")
	print "File opened"

	# Get a list of the windows that are open
	try:
		image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]
	except TypeError:
		raise TypeError("No windows open! Bio-formats failed. Check metadata for completeness.")
		return

#Checks to see if multiple windows are open. There should only be one hyperstack. If there are multiple, it will close windows with a single frame (because it sees them as partial slices).
# If you have single z-stack data but somehow also have a partial slice, this might close everything (seems like a rare situation though).
	if len(image_titles) > 1:
		for i in image_titles:
			print i
			imp = WindowManager.getImage(i)
			if imp.getNFrames() == 1: # If it is a partial slice, will close it
				imp.close()
	try:
		image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]
	except TypeError:
		raise Exception("No windows open! Is this a single slice acquisition?")
		return
	imp = IJ.getImage()
	imp.setTitle(basename + "_raw.tif")
	return basename

# checks for single plane acquisition. Don't need since you ask up front
def single_plane_check():
	print "Checking for z-planes..."
	imp = IJ.getImage()
	if imp.getNSlices() > 1:
		print "The number of z-planes is ", imp.getNSlices()
		singleplane = False

	elif imp.getNSlices() == 1:
		print "The number of z-planes is ", imp.getNSlices()
		singleplane = True

	return singleplane

# make_MAX checks for multi-z plane images and makes MAX projections if it finds them.
def make_MAX(singleplane): # singleplane is Boolean True/False
	image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]

	for i in image_titles:
		imp = WindowManager.getImage(i)
		if singleplane == False: # If the data is not single z-plane, runs max projection
			IJ.run(imp, "Z Project...", "projection=[Max Intensity] all")
			imp = WindowManager.getImage("MAX_" + i)
			windowName = imp.getTitle()
			IJ.saveAsTiff(imp, os.path.join(saveFolder,windowName)) #saves to saveFolder
			imp = WindowManager.getImage(i) # Gets the original hyperstack
			imp.changes = False # Answers "no" to the dialog asking if you want to save any changes
			imp.close() # Closes the hyperstack

		# If the data is single plane, it skipes projection and moves to LUT setting
		elif singleplane == True:
			windowName = imp.getTitle()
			print "Single plane data detected. Skipping Z-projection for ", windowName

# run_it is the main function that calls all the other functions
# This is the place to comment out certain function calls if you don't have a need for them
def run_it():
	# Make an error log file that can be written to
	errorFilePath = os.path.join(experimentFolder, "errorFile.txt")
	now = datetime.datetime.now()
	errorFile = open(errorFilePath, "w")
	errorFile.write("\n" + now.strftime("%Y-%m-%d %H:%M") + "\n")
	errorFile.write("#### anilyze-data ####" + "\n")
	errorFile.close()

	#Runs microscope_check and defines the scanList accordingly
	microscopeType = microscope_check(experimentFolder)

	# Call list_scans and pass it the microscopeType variable. Gets the scanList
	if microscopeType == "Olympus":
		scanList = list_scans(experimentFolder, microscopeType)
		print "The returned scanList is", len(scanList), "item(s) long"

	elif microscopeType == "Bruker":
		scanList = list_scans(experimentFolder, microscopeType)
		print "The returned scanList is", len(scanList), "item(s) long"

	# For each scan in the scanList, call the following functions:
	for scan in scanList:
		try:
			basename = os.path.basename(scan) # get the scan name (basename)

			#start new line in errorFile
			errorFile = open(errorFilePath, "a")
			errorFile.write("\n \n -- Processing " + basename + " --" + "\n")
			errorFile.close()

			make_hyperstack(basename, scan, microscopeType) # open the hyperstack
			imp = IJ.getImage() # select the open image
			channels = imp.getNChannels() #gets the number of channels
			print "The number of channels is", channels
			
			singleplane = single_plane_check() #checks to see if sinegle z-plane
			print "The returned value of singleplane is ", singleplane
			
			make_MAX(singleplane) # make max projection (skips if singleplane == True)

			IJ.run("Close All")

			#finishes errorFile
			errorFile = open(errorFilePath, "a")
			errorFile.write("Congrats, it was successful!\n")
			errorFile.close()
			IJ.freeMemory() # runs garbage collector

		except:  #if there is an exception to the above code, create or append to an errorFile with the traceback
			print "Error with ", basename, "continuing on..."
			errorFile = open(errorFilePath, "a")
			errorFile.write("\n" + now.strftime("%Y-%m-%d %H:%M") + "\n") #writes the date and time
			errorFile.write("Error with " + basename + "\n" + "\n")
			traceback.print_exc(file = errorFile) # writes the error traceback to the file
			errorFile.close()
			
			IJ.run("Close All")
			IJ.freeMemory() # runs garbage collector
			continue # continue on with the next scan, even if the current one threw an error
	
	#close out errorFile
	errorFile = open(errorFilePath, "a")
	errorFile.write("\nDone with script.\n")
	errorFile.close()

run_it()
print "Done with script"
