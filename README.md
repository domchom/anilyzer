# Anilyzer

This script uses Fiji/ImageJ to batch import, max project (if applicable) and save multi-z or single optical plane movies. It was built to deal with data structure from Bruker Prairie microscopes or Olympus Fluoview microscopes, however can be pretty easily modified to accomodate others. 

## Dependencies
As stated above, this script assumes a particular file heirarchy, that is either:
* **Bruker Style:** A parent directory containing sub-directories for each movie. Inside each sub-directory, individual .tif files ending in a suffix of *"_Cycle0000?_Ch?_00000?.ome.tif"* and a single .xml file containing metadata.
  * **NOTE:** If using the Bruker pipeline, your sub-directories **MUST** have the same base name as the .tif and .xml files inside! If you wish to rename things, you must do it after you have used this script. 
* **Olympus Style:** A parent directory containing sub-directories for each movie, along with a single .oif file.  


## Steps to run
1. Clone this repository to your computer or download the code however you wish.
2. Launch Fiji and open the script in the script editor.
3. Click "Run".
4. In the GUI window, select the location of your microscopy movies.
5. Select "Open".

## Script stages
1. The script makes an error file in the location you chose that reports any issues with processing.
2. The script determines the microscope type from the file structure.
3. The script gets a list of all the movies in the folder.
4. For each movie in the list the script:
   * Imports the file using bioformats importer.
   * Checks to see if the movie is a multi-z stack or single optical plane.
   * If multi-z, the script makes a maximum projection. If not, the script skips this step.
   * The max projection (or single plane image) is then saved to a folder called "processed". 
6. If the script encounters an error, it tries it's best to log it in the error file and move on.
7. When the script is finished, it will print "Done with Script" to the terminal window.

## Troubleshooting
Please let me know if you are getting a particular error, but here are a few I know to cause problems:
1. If using the Bruker style (multi .tifs) and you manually stopped the microscope in the middle of a stack, this can cause the .XML file to be incomplete. The script called bioformats independently of the .XML file, but since it looks to the .XML for metadata, this can sometimes cause the import to fail. This issue can be resolved by going into the .XML and manually deleting the lines corresponding to the incomplete stack. 
2. If you renamed your movie folders, this can sometimes cause an error because for the Bruker pipeline, the script gets a list of all the movie folders and then goes to look for .tif files of the same name. If the folder and file names do not match, it will not find anything to import!




