Anilyzer is a Python script that uses Fiji/ImageJ to batch import, max project (if applicable), and save multi-z or single optical plane movies. This tool was designed to process data from Bruker Prairie or Olympus Fluoview microscopes, but it can be easily modified to accommodate other data structures.
Dependencies

This script assumes a particular file hierarchy, either:

    Bruker Style: A parent directory containing sub-directories for each movie. Inside each sub-directory, individual .tif files ending in a suffix of "_Cycle0000?_Ch?_00000?.ome.tif" and a single .xml file containing metadata.
        NOTE: If using the Bruker pipeline, your sub-directories MUST have the same base name as the .tif and .xml files inside! If you wish to rename things, you must do it after using this script.
    Olympus Style: A parent directory containing sub-directories for each movie, along with a single .oif file.

How to Run

    Clone this repository to your computer or download the code however you wish.
    Launch Fiji and open the script in the script editor.
    Click "Run".
    In the GUI window, select the location of your microscopy movies.
    Select "Open".

Script Stages

    The script makes an error file in the location you chose that reports any issues with processing.
    The script determines the microscope type from the file structure.
    The script gets a list of all the movies in the folder.
    For each movie in the list, the script:
        Imports the file using Bioformats importer.
        Checks to see if the movie is a multi-z stack or single optical plane.
        If multi-z, the script makes a maximum projection. If not, the script skips this step.
        The max projection (or single plane image) is then saved to a folder called "processed".
    If the script encounters an error, it logs it in the error file and moves on.
    When the script finishes, it prints "Done with Script" to the terminal window.

Troubleshooting

Please let me know if you encounter any errors, but here are a few common ones:

    If using the Bruker style (multi .tifs) and you manually stopped the microscope in the middle of a stack, this can cause the .XML file to be incomplete. The script calls Bioformats independently of the .XML file, but since it looks to the .XML for metadata, this can sometimes cause the import to fail. This issue can be resolved by going into the .XML and manually deleting the lines corresponding to the incomplete stack.
    If you renamed your movie folders, this can sometimes cause an error because, for the Bruker pipeline, the script gets a list of all the movie folders and then looks for .tif files with the same name. If the folder and file names do not match, it will not find anything to import!