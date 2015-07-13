"""
I/O stuff adapted from example script
"""

import os

image_extension = ".fits"
datafile_extension = ".dat"


def get_filenames(path):
    """ Searches a directory and its subdirectories (one level deep) for all image files to process.
        
        Requires: path <string> (Base directory to search in)
                                          
        Returns: <list of strings> (Roots of all images, without their extensions.)
    """
    
    filenames = []
    
    # Start in the base path
    files_and_dirs_in_path = os.listdir(path)

    for file_or_dir_name in files_and_dirs_in_path:
        
        joined_name = os.path.join(path,file_or_dir_name)
        
        # Check if this is a file
    
        if os.path.isfile(joined_name):
            if( is_good_image(joined_name) ):
                filenames.append(joined_name.replace(image_extension,""))
        else:
            
            # This is a directory, so let's go into it and look for files there
            files_and_dirs_in_subpath = os.listdir(joined_name)
            
            for file_or_dir_in_subpath in files_and_dirs_in_subpath:
                subjoined_name = os.path.join(joined_name,file_or_dir_in_subpath)
                
                if( is_good_image(subjoined_name) ):
                    filenames.append(subjoined_name.replace(image_extension,""))
    
    return filenames


def is_good_image(filename):
    """ Determines whether a filename corresponds to an image file for which there is also a
        corresponding data file.
        
        Requires: filename <string>
        
        Returns: <bool>
    """
    
    if image_extension not in filename:
        return False
    
    test_datafile_name = filename.replace(image_extension,datafile_extension)
    
    return os.path.isfile(test_datafile_name)
    
 

def imagefile(filename):
	return filename + image_extension


def datafile(filename):
	return filename + datafile_extension


def workprefix(filename, workdir):
	"""
	Returns a path to the workdir that can be used as prefix for megalut-internal files
	"""
	return os.path.join(workdir, "-".join(filename.split("/")[-2:]))
	
	
