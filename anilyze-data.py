# @File(label = "Input directory", style = "directory") input_dir

"""
AUTHOR: Ani Michaud (Varjabedian) / Dominic Chomchai
DESCRIPTION: This branch of code is a based on the Anilyzer. Its primary function is to open hyperstacks, 
perform a maximum projection on all images, and save the output in a designated folder.

The code is organized in the following manner:

    Script parameters are located at the top, preceded by a "#@" symbol, to gather information for the dialogue box.
    Import statements for all necessary modules are included.
    The main functions for processing data are defined.
    The "run_it()" function is implemented, which sets up error logging and calls all the other processing functions. 
        This function should eventually be moved to its own file, but for now, it is kept in the same file for ease of access.

To understand the overall flow of events, check the order of calls in the "run_it()" function. If you wish to skip certain steps, 
you can comment them out in the "run_it()" function, but please note that some functions pass arguments to each other, so commenting 
out specific functions may result in errors. It's best to read the individual function before commenting it out to avoid any potential errors.

For more information and the latest updates, please visit the GitHub repository at: https://github.com/anivarj/anilyzer.

Update 230417: Dom modified the script to make it more readable and to remove superfluous code. Dom also added functionality to 
detect whether the imported images are single Z-stacks (with no time element), and import those correctly.
"""
import os
import glob
import shutil
import datetime
import traceback
from ij import IJ, WindowManager

save_max_projection = True

# Convert input directory to string
input_dir = str(input_dir)

def microscope_check(input_dir):
    """
    Check the microscope type by looking for ".oif" files in the input directory.
    If one or more ".oif" files are found, assume the microscope is an Olympus.
    Otherwise, assume the microscope is a Bruker.

    Args:
    - input_dir (str): The path to the directory to check for ".oif" files.

    Returns:
    - microscope_type (str): The type of microscope detected.
    """
    for file in os.listdir(input_dir):
        if os.path.splitext(file)[-1] == ".oif":
            microscope_type = "Olympus"
            break
    else:
        microscope_type = "Bruker"
    return microscope_type

def list_scans(input_dir, microscope_type):
    """
    List all the scans in the input directory, based on the microscope type.
    For Bruker microscopes, scans are directories with no extension.
    For Olympus microscopes, scans are directories ending with ".oif.files".

    Args:
    - input_dir (str): The path to the directory containing the scans.
    - microscope_type (str): The type of microscope used to acquire the scans.

    Returns:
    - scan_list (list): A list of directories containing the scans.
    """
    if microscope_type == "Bruker":
        # Use glob to find directories with no extension
        file_pattern = os.path.join(input_dir, "*")
        scan_list = [os.path.join(input_dir, f) for f in glob.glob(file_pattern) if os.path.isdir(f)]
    elif microscope_type == "Olympus":
        # Use glob to find directories ending with ".oif.files"
        file_pattern = os.path.join(input_dir, "*.oif.files")
        scan_list = glob.glob(file_pattern)
    return scan_list

def load_initiator_file(input_dir, scan, microscope_type, basename):
    """
    Load the initiator file for a given microscope type and determine the image type.

    Args:
        input_dir (str): The input directory.
        scan (str): The scan directory for Bruker microscope type.
        microscope_type (str): The type of microscope, either "Olympus" or "Bruker".
        basename (str): The basename of the file for Olympus microscope type.

    Raises:
        TypeError: If the microscope type is unknown.

    Returns:
        A tuple containing the initiator file path and the image type, either "t-series" or "z-stack".
    """
    if microscope_type == "Olympus":
        # Use the .oif file as initiator
        initiator_file_name = os.path.splitext(basename)[0]
        initiator_file_path = os.path.join(input_dir, initiator_file_name)

        # Determine if the image type is a t-series or z-stack
        target_folder_name = initiator_file_path.split('/')[-1] + ".files"
        target_folder_path = os.path.join(input_dir, target_folder_name)

        # Check the name of the first .tif file to determine the image type
        target_folder_scan_list = [file for file in os.listdir(target_folder_path) if file.endswith(".tif")]
        first_file = target_folder_scan_list[0]
  
        # assign the image type
        if "T" in first_file.split('/')[-1]:
            image_type = "t-series"
        else:
            image_type = "z-stack"

    elif microscope_type == "Bruker":
        # Use the first TIF file as initiator
        initiator_file_name = basename + "_Cycle00001_Ch?_000001.ome.tif"
        initiator_file_path = glob.glob(os.path.join(scan, initiator_file_name))
        initiator_file_path = initiator_file_path[0]

        # Determine if the image type is a t-series or z-stack
        target_folder_scan_list = [file for file in os.listdir(scan) if file.endswith(".tif")]

        # Check the name of the last .tif file to determine the image type
        last_file = target_folder_scan_list[-1]
        last_file = last_file.split('/')[-1]
        cycle_part = last_file.split('_')[-3]

        # assign the image type
        if int(cycle_part[5:]) != 1:
            image_type = "t-series"
        else:
            image_type = "z-stack"

    else:
        raise TypeError("Unknown microscope type " + microscope_type)
        
    return initiator_file_path, image_type

def make_hyperstack(initiator_file_path, basename, image_type, save_folder):
    """
    Convert the initiator file to a hyperstack and save it as a TIFF file.

    Args:
        initiator_file_path (str): The path to the initiator file.
        basename (str): The basename of the file.
        image_type (str): The type of the image, either "t-series" or "z-stack".
        save_folder (str): The folder where the hyperstack will be saved.

    Raises:
        Exception: If there are no windows open or more than one window is open.

    Returns:
        None.
    """
    if image_type == "z-stack":
        IJ.run("Bio-Formats Importer", "open=[" + initiator_file_path + "] color_mode=Grayscale concatenate_series open_all_series quiet rois_import=[ROI manager] view=Hyperstack stack_order=XYCTZ")
        imp = IJ.getImage()
        windowName = imp.getTitle()
        IJ.saveAsTiff(imp, os.path.join(save_folder,basename + ".tif"))

    else:
        # Import the initiator file as a hyperstack using Bio-Formats
        IJ.run("Bio-Formats Importer", "open=[" + initiator_file_path + "] color_mode=Grayscale concatenate_series open_all_series quiet rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT")
        
        # Check to see if multiple windows are open. 
        image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]
        if len(image_titles) > 1:
            for i in image_titles:
                imp = WindowManager.getImage(i)
                if imp.getNFrames() == 1: # If it is a single frame, close it (because it sees them as partial slices)
                    imp.close()
            image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]
            if len(image_titles) != 1:
                raise Exception("No windows open! Is this a single slice acquisition?")
        
        imp = IJ.getImage()
        imp.setTitle(basename + "_raw.tif")

def single_plane_check():
    '''
    Checks if the currently selected image in ImageJ is a single z-plane or not. 
    It returns a boolean value indicating whether the image is a single z-plane or not.

    Args: 
    None.

    Returns:
    - singleplane (bool): True if the selected image is a single z-plane, False otherwise.
    '''
    imp = IJ.getImage()
    singleplane = True if imp.getNSlices() == 1 else False
    return singleplane

def make_MAX(singleplane, save_folder):
    """
    Create a maximum intensity projection of each image window and save it as a separate TIFF file.

    Args:
    - singleplane (bool): Whether the images are single-plane or multiplane.

    Returns:
    None.
    """
    image_titles = [WindowManager.getImage(id).getTitle() for id in WindowManager.getIDList()]

    for title in image_titles:
        imp = WindowManager.getImage(title)
        
        if singleplane == False and save_max_projection == True: 
            IJ.run(imp, "Z Project...", "projection=[Max Intensity] all") # Run Z projection and save MAX image
            max_imp = WindowManager.getImage("MAX_" + title)
            windowName = max_imp.getTitle()
            windowName = windowName.replace(".oif.files", "")
            IJ.saveAsTiff(max_imp, os.path.join(save_folder, windowName))
            imp = WindowManager.getImage(title)
            imp.changes = False # Answers "no" to the dialog asking if you want to save any changes
            imp.close() # Closes the hyperstack
            print "Saving Max Projection for ", windowName
            
        elif singleplane == False and save_max_projection == False:
            windowName = imp.getTitle()
            windowName = windowName.replace(".oif.files", "")
            IJ.saveAsTiff(imp, os.path.join(save_folder, windowName))
            print "Saving hyperstack for ", windowName
        
        else:
            windowName = imp.getTitle()
            print "Single plane data detected. Skipping Z-projection for ", windowName


def run_it(input_dir):
    """
    Runs the main pipeline for processing images from either an Olympus or Bruker microscope.

    Creates an error log file and determines the microscope type and scan list.
    Creates an output directory for processed images and for each scan in the scan list,
    it calls the make_hyperstack() and make_MAX() functions.
    If an error occurs, it writes the error message to the error log file and continues with the next scan.
    After all scans are processed, it moves all existing folders into a new folder and closes the error log file.
    """
    # Create an error log file
    error_file_path = os.path.join(input_dir, "errorFile.txt")
    now = datetime.datetime.now()
    with open(error_file_path, "w") as error_file:
        error_file.write("\n" + now.strftime("%Y-%m-%d %H:%M") + "\n")
        error_file.write("#### anilyze-data ####" + "\n")

    # Determine microscope type and scan list
    microscope_type = microscope_check(input_dir)
    scan_list = list_scans(input_dir, microscope_type)
    print "The returned scanList is", len(scan_list), "item(s) long"
    
    # Create output directory for processed images
    save_folder = os.path.join(input_dir, "processed")
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    for scan in scan_list:
        try:
            basename = os.path.basename(scan)
            print "Processing " + basename
            with open(error_file_path, "a") as error_file:
                error_file.write("\n \n -- Processing " + basename + " --" + "\n")

            # Load initiator file and create hyperstack
            initiator_file_path, image_type = load_initiator_file(input_dir, scan, microscope_type, basename)
            make_hyperstack(initiator_file_path, basename, image_type, save_folder)

            # Create MAX projection and save as TIFF file if it is not singleplane or single z-stack
            if image_type == "t-series":
                singleplane = single_plane_check()
                make_MAX(singleplane, save_folder)

            # Close all open windows and free memory
            IJ.run("Close All")
            IJ.freeMemory()

            print "Processing " + basename + " was successful!"
            with open(error_file_path, "a") as error_file:
                error_file.write("Congrats, it was successful!\n")

        except Exception as e:
            print "Error with ", basename, "continuing on..."
            with open(error_file_path, "a") as error_file:
                error_file.write("\n" + now.strftime("%Y-%m-%d %H:%M") + "\n")
                error_file.write("Error with " + basename + "\n" + "\n")
                traceback.print_exc(file=error_file)
            
            # Close all open windows and free memory
            IJ.run("Close All")
            IJ.freeMemory()
            continue

    # Move all existing folders into a new folder
    scope_folder = os.path.join(input_dir, 'scope_folders')
    if not os.path.exists(scope_folder):
        os.mkdir(scope_folder)
    for folder in os.listdir(input_dir):
        folder_path = os.path.join(input_dir, folder)
        if os.path.isdir(folder_path) and folder not in [scope_folder, 'processed']:
            shutil.move(folder_path, scope_folder)

    # Move all existing oif files into a new folder
    for file in os.listdir(input_dir):
        if file.endswith('.oif'):
            file_path = os.path.join(input_dir, file)
            shutil.move(file_path, os.path.join(scope_folder, file))

    # Close the error log file
    with open(error_file_path, "a") as error_file:
        error_file.write("\nDone with script.\n")
        
    print "Done with script"

run_it(input_dir)