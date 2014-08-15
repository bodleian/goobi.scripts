import os 
import sys 
import string 
import subprocess 
import logging
import glob
import traceback
import re
import Image #Python Image Library
#from jpylyzer import *


__all__ = ["fnmatch","fnmatchcase","translate"]

_cache = {}

def verify_jp2(file):
	jp2Element = checkOneFile(file)
	if jp2Element.findtext('isValidJP2') == 'True':
		return True
	else:
		return False
		
def fnmatch(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are first case-normalized
    if the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """

    import os
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    return fnmatchcase(name, pat)

def fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.
    """

    if not _cache.has_key(pat):
        res = translate(pat)
        _cache[pat] = re.compile(res)
    return _cache[pat].match(name) is not None

def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            res = res + '.*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + "$"

def initiate_log(logfile_name=None, logfile_directory=None):
    """ Initiates python's logging module

    Parameters:
    logfile_name = the name of the log file (default 'log.txt')
    logfile_directory = location of log file (default current working directory)

    """
    if logfile_name is None:
        logfile_name = 'log.txt'
    if logfile_directory is None:
        logfile_directory = os.getcwd()
    logfile = path_file_combine(logfile_directory, logfile_name)
    logging.basicConfig(filename=logfile, level=logging.DEBUG)


def path_file_combine(path, name):
    """Returns normalised filename combined with path.

    Keeps scripts platform independent.
    
    """
    filepath = os.path.normpath(path)
    filename = os.path.normpath(name)
    combined = os.path.join(filepath, filename)
    return combined

def initiate_log(logfile_name=None, logfile_directory=None):
    """ Initiates python's logging module

    Parameters:
    logfile_name = the name of the log file (default 'log.txt')
    logfile_directory = location of log file (default current working directory)

    """
    if logfile_name is None:
        logfile_name = 'log.txt'
    if logfile_directory is None:
        logfile_directory = os.getcwd()
    logfile = path_file_combine(logfile_directory, logfile_name)
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

def true_colour_convert(file_name, directory_name=None):
    """ Decompress image file and convert in place to uncompressed 8-bit-per-channel truecolour files, replacing existing file.
    
    Parameters:
    directory_name = where the source file is (defaults to none - assumes file_name includes path)
    file_name = name of the source file
    
    N.B. superceded by the source file format sensitive jp2 conversion in compress_jp2() function.
    so not strictly needed prior to jpeg2000 conversion.
    
    """
    
    if directory_name is not None:
        image_file = path_file_combine(directory_name, file_name)
    else:
        image_file = os.path.normpath(file_name)
        
    if os.access(image_file, os.W_OK):
        action = 'mogrify -strip -compress none -depth 8 -type truecolor -identify -alpha off ' + image_file #order of operations import here if images are to work with Djatoka after a jp2 conversion
#        action2 = 'mogrify -alpha off -identify ' + image_file #order of operations import here if images are to work with Djatoka after a jp2 conversion
        q = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        q.wait()
        if q.returncode != 0:
            logging.error('failed with return code: %s', q.returncode)
            raise Exception('Mogrify failed', image_file)
        else:
            logging.info('%s success', image_file)
            print action
            return q.returncode    
 #       z = subprocess.Popen(action2, shell=True, stdout=subprocess.PIPE)
 #       z.wait()
 #       if z.returncode != 0:
 #           logging.error('failed with return code: %s', z.returncode)
 #           raise Exception('Mogrify failed', image_file)
 #       else:
 #           logging.info('%s success', image_file)
 #           print action2
 #           return z.returncode    
    else:
        logging.error('Could not access file %s', image_file)
        raise Exception('Could not access file', image_file)

def gm_true_colour_convert(file_name, directory_name=None):
    """ Decompress image file and convert in place to uncompressed 8-bit-per-channel truecolour files, replacing existing file.
    
    Parameters:
    directory_name = where the source file is (defaults to none - assumes file_name includes path)
    file_name = name of the source file
    
    N.B. superceded by the source file format sensitive jp2 conversion in compress_jp2() function.
    so not strictly needed prior to jpeg2000 conversion.
    
    """
    
    if directory_name is not None:
        image_file = path_file_combine(directory_name, file_name)
    else:
        image_file = os.path.normpath(file_name)
        
    if os.access(image_file, os.W_OK):
        action = 'gm mogrify -compress none -depth 8 -type truecolor -monitor ' + image_file #order of operations import here if images are to work with Djatoka after a jp2 conversion
#        action2 = 'mogrify -alpha off -identify ' + image_file #order of operations import here if images are to work with Djatoka after a jp2 conversion
        q = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        q.wait()
        if q.returncode != 0:
            logging.error('failed with return code: %s', q.returncode)
            raise Exception('Mogrify failed', image_file)
        else:
            logging.info('%s success', image_file)
            print action
            return q.returncode    
 #       z = subprocess.Popen(action2, shell=True, stdout=subprocess.PIPE)
 #       z.wait()
 #       if z.returncode != 0:
 #           logging.error('failed with return code: %s', z.returncode)
 #           raise Exception('Mogrify failed', image_file)
 #       else:
 #           logging.info('%s success', image_file)
 #           print action2
 #           return z.returncode    
    else:
        logging.error('Could not access file %s', image_file)
        raise Exception('Could not access file', image_file)


def jp2_piped_colour_convert(file_name, directory_name=None):
    """ Decompress image file and convert to uncompressed 8-bit-per-channel truecolour files, then pipe via a temporary file in ram-backed storage to kakadu.
    
    Parameters:
    directory_name = where the source file is (defaults to none - assumes file_name includes path)
    file_name = name of the source file
    
    N.B. Uses graphicsmagick rather than imagemagick which is, in most cases, 40 - 50 % faster.
    
    """
    
    if directory_name is not None:
        image_file = path_file_combine(directory_name, file_name)
    else:
        image_file = os.path.normpath(file_name)


    temp_output = '/tmp/temp.tif'
    jp2_file = image_file.replace('.tif', '.jp2')
    
    if os.access(image_file, os.W_OK):
        action = 'gm convert -compress none -depth 8 ' + image_file + ' ' + temp_output  + ' ; /opt/kakadu/kdu_compress -i ' +  "'" + temp_output + "'" + ' -o ' + "'" + jp2_file + "'" + ' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024;'
#order of operations import here if images are to work with Djatoka after a jp2 conversion
        q = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        q.wait()
        if q.returncode != 0:
            logging.error('failed with return code: %s', q.returncode)
            raise Exception('Image conversion failed', os.path.abspath(image_file))
        else:
			if verify_jp2(jp2_file) is True:
				print 'OK: ' + os.path.abspath(jp2_file)
				logging.info('%s verifies correctly', os.path.abspath(jp2_file))
			else:
				print 'FAIL: ' + jp2_file
				logging.error('Could not verify the jpeg2000 file %s', os.path.abspath(jp2_file))
				raise Exception('Could not verify the jpeg2000 file', os.path.abspath(jp2_file))  
    else:
        logging.error('Could not access file %s', os.path.abspath(image_file))
        raise Exception('Could not access file', os.path.abspath(image_file))
  

    

                
def eight_bit_convert(file_name, directory_name=None):
    """ Decompress image file and convert in place to uncompressed 8-bit-per-channel files, replacing existing file.
    
    Parameters:
    directory_name = where the source file is (defaults to none - assumes file_name includes path)
    file_name = name of the source file
    
    N.B. superceded by the source file format sensitive jp2 conversion in compress_jp2() function.
    so not strictly needed prior to jpeg2000 conversion.
    
    """
    
    if directory_name is not None:
        image_file = path_file_combine(directory_name, file_name)
    else:
        image_file = os.path.normpath(file_name)
        
    if os.access(image_file, os.W_OK):
        action = 'mogrify -compress none -depth 8 ' + image_file #order of operations import here if images are to work with Djatoka after a jp2 conversion
        q = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        q.wait()
        if q.returncode != 0:
            logging.error('failed with return code: %s', q.returncode)
            raise Exception('Mogrify failed', image_file)
        else:
            logging.info('%s success', image_file)
            print action
            return q.returncode    
    else:
        logging.error('Could not access file %s', image_file)
        raise Exception('Could not access file', image_file)

def compress_jp2_basic(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """ Convert to lossless jp2, treats all files the same. Does not handle colour conversion of greyscale and bitonal files.
    
    takes tiff file and outputs jp2 - if done on monochrome jpeg2000s will produce monochrome jpeg2000s, which Djatoka's expansion command won't like [it expands to .ppm, not .pgm or .pbm]
    
    Parameters:
    source_directory - where the tiffs are (default none - in which case expect file_name to include path information)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    """ 
    if master_extension is None:
        master_extension = '.tif'
    if derivative_extension is None:
        derivative_extension = '.jp2'
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory

    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)
     
    print input_file
    
    if destination_directory is not None:
        output_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
    else:
        output_file = input_file.replace(master_extension,derivative_extension)
        
    if (os.access(input_file, os.R_OK)) and (os.access(os.path.dirname(output_file),os.W_OK)):## check file exists
        action = '/opt/kakadu/kdu_compress -i ' +  "'" + input_file + "'" + ' -o ' + "'" + output_file + "'" + ' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024'
        p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        p.wait()
        if p.returncode != 0:
            logging.error('failed with return code: %s', p.returncode)
            print 'Conversion failed \n'
            print 'Tried ' + action
            return p.returncode
        else:
            logging.info('%s jp2 conversion success', input_file)
            print action
            return p.returncode
    else:
        logging.error('Could not access %s or write to directory %s', input_file, os.path.dirname(output_file))
        return 1


def check_corresponding_file(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """ checks if a file with one extension has a corresponding file with a different extension, in some directory or other.

    e.g. checks that each tiff in a source directory has a corresponding jpeg2000 in destination directory
    if not, carries out action.
    
    Parameters:
    source_directory - where the tiffs are (default none - in which case expect file_name to include path information)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    
    """
    
    if master_extension is None:
        master_extension = 'tif'
    if derivative_extension is None:
        derivative_extension = 'jp2'
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory

    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        input_file = os.path.normpath(file_name)
        
    if destination_directory is not None:
        corresponding_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
    else:
        corresponding_file = input_file.replace(master_extension,derivative_extension)
    
    #check if the corresponding file is readable    
    if file_name[-3:] == master_extension:
        if  os.access(corresponding_file, os.R_OK):
            return True
        else:
            return False
    
def get_image_data(file_name, source_directory=None):
    """Use python image library to get image file properties and return as array. For JP2s see: 

    Parameters:
    file_name - name of image file
    source_directory - location of file (default None - if so, assumes file_name includes relevant path information)

    Output:
    array with [format, mode, size]
    mode - L = greyscale, 1 = bitonal, RGB = colour
    
    """
    
    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)
        
    image_x = Image.open(input_file)
    image_properties = [image_x.format, image_x.mode, image_x.size] 
    return image_properties

def compress_jp2(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """Convert to lossless jp2. Handles colour conversion of greyscale and bitonal files to 3 colour channels of information.
    
    Takes tiff file and outputs jp2, compatible with Djatoka
    
    For greyscale and bitonal images the same input is copied to each of the 
    three colour channels, with no colour palette applied, to create a 24-bit 
    [3 x 8] image which will decode to ppm for Djatoka.
    
    Parameters:
    source_directory - where the tiffs are (default none, in which case assumes path information in file_name)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    """

    if master_extension is None:
        master_extension = 'tif'
    if derivative_extension is None:
        derivative_extension = 'jp2'
        
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory
    
    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)
    
    if destination_directory is not None:
        output_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
    else:
        output_file = input_file.replace(master_extension,derivative_extension)

    print 'Input file is: ' + input_file
    
    print 'Output file is:' + output_file
    
    if (os.access(input_file, os.R_OK)) and (os.access(os.path.dirname(output_file),os.W_OK)):## check file exists
        print 'Can access ' + input_file
        image_data = get_image_data(file_name, source_directory) #get properties of image
        image_mode = image_data[1] #colour mode of image
        if image_mode == 'L': #greyscale
            action = '/opt/kakadu/kdu_compress -i ' + "'" + input_file + "'" + ',' + "'" + input_file + "'" + ',' + "'" + input_file + "'" + ' -no_palette -o ' + "'" + output_file + "'" +' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024 -num_threads 4'
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('failed with return code: %s', p.returncode)
                print "Conversion failed \n"
            else:
                print action
                return 0
        elif image_mode == '1': #Bitonal  
            action = '/opt/kakadu/kdu_compress -i ' + "'" + input_file + "'" + ',' + "'" + input_file + "'" + ',' + "'" + input_file + "'" + ' -no_palette -o ' + "'" + output_file + "'" + ' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024 -num_threads 4'
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('failed with return code: %s', p.returncode)
                print "Conversion failed \n"
            else:
                print action
                return 0
        elif image_mode == 'RGB': #RGB colour  
            #action = '/opt/kakadu/kdu_compress -i '  + "'" + input_file + "'" + ' -o ' +  "'" + output_file + "'" + ' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024 -num_threads 4'
            action = '/opt/kakadu/kdu_compress -i ' +  "'" + input_file + "'" + ' -o ' + "'" + output_file + "'" + ' -jp2_space sRGB -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024'
            print action
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('failed with return code: %s', p.returncode)
                print "Conversion failed \n"
            else:
                print action
                return 0
        else:
            print "Could not identify image colour mode.\n"
            logging.error("%s conversion : UNKNOWN MODE", input_file)
            return 1
    else:
        logging.error('Could not access %s or write to directory %s', input_file, destination_directory)
        return 1

def compress_jp2_colour(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """Convert to lossless jp2. Handles colour conversion of greyscale and bitonal files to 3 colour channels of information.
    
    Takes tiff file and outputs jp2, compatible with Djatoka
    
    For greyscale and bitonal images the same input is copied to each of the 
    three colour channels, with no colour palette applied, to create a 24-bit 
    [3 x 8] image which will decode to ppm for Djatoka.
    
    Parameters:
    source_directory - where the tiffs are (default none, in which case assumes path information in file_name)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    """

    if master_extension is None:
        master_extension = 'tif'
    if derivative_extension is None:
        derivative_extension = 'jp2'
        
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory
    
    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)

    if destination_directory is not None:
#        jpeg_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
        jp2_file = destination_directory + '/' + os.path.basename(file_name).replace(master_extension,derivative_extension)
    else:
        jp2_file = source_directory + '/' + os.path.basename(file_name).replace(master_extension,derivative_extension)
    

    print 'Input file is: ' + input_file
    
    print 'Output file is:' + jp2_file
    
    if (os.access(input_file, os.R_OK)) and (os.access(os.path.dirname(jp2_file),os.W_OK)):## check file exists
        #print 'Can access ' + input_file
        #action = '/opt/kakadu/kdu_compress -i '  + "'" + input_file + "'" + ' -o ' +  "'" + output_file + "'" + ' -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024 -num_threads 4'
        action = '/opt/kakadu/kdu_compress -i ' +  "'" + input_file + "'" + ' -o ' + "'" + jp2_file + "'" + ' -jp2_space sRGB -rate - Creversible=yes Clevels=6 "Cprecincts={256,256},{256,256},{128,128}" Corder="RPCL" ORGgen_plt=yes ORGtparts="R" Cblk="{64,64}" Cuse_sop=yes Cuse_eph=yes -flush_period 1024'
        #print action
        p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        p.wait()
        if p.returncode != 0:
            logging.error('failed with return code: %s', p.returncode)
            print "Conversion failed \n"
        else:
            print "Conversion passed \n"
	#		if verify_jp2(jp2_file) is True:
	#			print 'OK: ' + os.path.abspath(jp2_file)
	#			logging.info('%s verifies correctly', os.path.abspath(jp2_file))
	#		else:
	#			print 'FAIL: ' + jp2_file
	#			logging.error('Could not verify the jpeg2000 file %s', os.path.abspath(jp2_file))
	#			raise Exception('Could not verify the jpeg2000 file', os.path.abspath(jp2_file))  
    else:
        logging.error('Could not access %s or write to directory %s', input_file, destination_directory)
        return 1

def compress_jpeg(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """Convert to jpeg.

    Parameters:
    source_directory - where the tiffs are (default none, in which case assumes path information in file_name)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    """

    if master_extension is None:
        master_extension = 'tif'
    if derivative_extension is None:
        derivative_extension = 'jpg'
        
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory
    
    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)
    
    if destination_directory is not None:
#        jpeg_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
        jpeg_file = destination_directory + '/' + os.path.basename(file_name).replace(master_extension,derivative_extension)
    else:
        jpeg_file = source_directory + '/' + os.path.basename(file_name).replace(master_extension,derivative_extension)


    print 'Jpeg file: ' + jpeg_file


    if (os.access(input_file, os.R_OK)) and (os.access(os.path.dirname(jpeg_file),os.W_OK)):## check file exists
        action = 'gm convert -format jpeg -resize 60% ' + input_file + '[0] ' + jpeg_file 
        #print action
        p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
        p.wait()
        if p.returncode != 0:
            logging.error('failed with return code: %s', p.returncode)
            print "Conversion failed \n"
        else:
            print 'OK: ' + os.path.abspath(jpeg_file)
    else:
        logging.error('Could not access %s or write to directory %s', input_file, destination_directory)
        return 1

    
def expand_jp2(file_name, source_directory=None,destination_directory=None, master_extension=None, derivative_extension=None, output_type=None, expand_parameters=None):
    """Convert FROM lossless jp2. Uses kdu_expand.
    
    takes jp2 file and outputs non-jp2 [usually tiff]
    
    Need improving to allow fine control over output image size, bit-depth, colour space, and so on.
    
    Parameters:
    source_directory - where the jpeg2000s are
    file_name - the jpeg2000 file name
    destination_directory - where to put the converted file (default sourcedirectory)
    master_extension - '.jp2' usually, but function should handle other input file formats (default .jp2)
    derivative_extension - '.tif' usually, but kdu_compress can create other jpeg2000 formats (default .tif)
    output_type - placeholder for output file type (default None)
    expand_parameters - additional parameters to pass to kdu_expand (default None)
    """
    
    if master_extension is None:
        master_extension = '.jp2'
    if derivative_extension is None:
        derivative_extension = '.tif'
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory

    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        if os.path.dirname(os.path.normpath(file_name)) != '':
            print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
            input_file = os.path.normpath(file_name)
        else:
            input_file = path_file_combine(os.getcwd(),file_name)
    
    print 'Input file: ' + input_file     
    if destination_directory is not None:
        output_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
    else:
        output_file = input_file.replace(master_extension,derivative_extension)
    
    print 'Output file: ' + output_file
    
    if (os.access(input_file, os.R_OK)) and (os.access(os.path.dirname(output_file),os.W_OK)):## check file exists and output folder is writeable
        if output_type is None:
            action = '/opt/kakadu/kdu_expand -i ' + input_file + ' -o ' + output_file
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('%s failed with return code: %s', input_file, p.returncode)
                print "Conversion failed \n"
                return p.returncode
            else:
                logging.info('%s success', input_file)
                print action
                return p.returncode
        elif output_type == 'L': #greyscale
            action = '/opt/kakadu/kdu_expand -i ' + input_file + ' -o ' + output_file
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('%s failed with return code: %s', input_file, p.returncode)
                print "Conversion failed \n"
                return p.returncode
            else:
                logging.info('%s success', input_file)
                print action
                # should add stage here for appropriate conversion to greyscale using mogrify on output_file
                return p.returncode
        elif output_type == '1': #Bitonal 
            action = '/opt/kakadu/kdu_expand -i ' + input_file + ' -o ' + output_file
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('%s failed with return code: %s', input_file, p.returncode)
                print "Conversion failed \n"
                return p.returncode
            else:
                logging.info('%s success', input_file)
                print action
                # should add stage here for appropriate conversion to group 4 compressed bitonal using mogrify on output_file 
                return p.returncode
        elif output_type == 'RGB': #RGB colour  
            action = '/opt/kakadu/kdu_expand -i ' + input_file + ' -o ' + output_file
            #same as None as RGB is the default, but we may want to add some other features here.
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                logging.error('%s failed with return code: %s', input_file, p.returncode)
                print "Conversion failed \n"
                return p.returncode
            else:
                logging.info('%s success', input_file)
                print action
                return p.returncode
    else:
        logging.error('Could not access %s or write to directory %s', input_file, os.path.dirname(output_file))
        raise Exception('Could not access file', input_file)
       
    
         
            
            
def delete_corresponding_file(file_name, source_directory=None, destination_directory=None, master_extension=None, derivative_extension=None):
    """Deletes file with one extension corresponding to file with another extension. e.g. deletes the jp2 that matches a particular tiff
    
    This function, and the check_correspond function are used for house cleaning
    for example, deleting all of the jpeg2000s to reconvert from tiff, or
    deleting all of the tiffs once the jpeg2000s have been created.
    
    Parameters:
    source_directory - where the tiffs are (default none - in which case expect file_name to include path information)
    file_name - the tiff file name
    destination_directory - where to put the converted file (default source_directory)
    master_extension - '.tif' usually, but function should handle other input file formats (default .tif)
    derivative_extension - '.jp2' usually, but kdu_compress can create other jpeg2000 formats (default .jp2)
    
    
    """
    
    if master_extension is None:
        master_extension = 'tif'
    if derivative_extension is None:
        derivative_extension = 'jp2'
    if (destination_directory is None) and (source_directory is not None):
        destination_directory = source_directory

    if source_directory is not None:
        input_file = path_file_combine(source_directory, file_name)
    else:
        input_file = os.path.normpath(file_name)
        
    if destination_directory is not None:
        corresponding_file = path_file_combine(destination_directory, file_name.replace(master_extension, derivative_extension))
    else:
        corresponding_file = input_file.replace(master_extension,derivative_extension)
    
    #check if the corresponding file is readable    
    if file_name[-3:] == master_extension:
        if  os.access(corresponding_file, os.R_OK):
            print 'Deleting file' + corresponding_file
            #os.unlink(derivative_file)
            return True
        else:
            return False


def get_jp2_data(file_name,output_directory=None,output_file=None):
    """Uses kdu_expand to get the file information - size, components, bitdepth, etc - from a jpeg2000 file. 
    
    Runs kdu_expand with the record option, which writes the header information to a text file. Script reads
    the text file, extracts the information and converts to an array/dictionary, then deletes the text file.
    
    Parameters:
    source_directory - where source file is
    file_name - the source file name
    output_directory - where to store the working text file, gets deleted after use (default current working directory)
    output_file - the name of the working text file, gets deleted after use  (default 'jp2.txt')
    
    Output:
    array with typically
    Sprofile=PROFILE2
    Scap=no
    Sextensions=0
    Ssize={5820,3352} - DIMENSIONS of image
    Sorigin={0,0}
    Stiles={5820,3352}
    Stile_origin={0,0}
    Scomponents=3 - COLOUR COMPONENTS
    Ssigned=no,no,no
    Sprecision=1,1,1 - BIT DEPTH
    Ssampling={1,1},{1,1},{1,1}
    Sdims={5820,3352},{5820,3352},{5820,3352}
    Cycc=no
    Cmct=0
    Clayers=1 - QUALITY LAYERS
    Cuse_sop=yes
    Cuse_eph=yes
    Corder=RPCL
    Calign_blk_last={no,no}
    Clevels=6 - RESOLUTION LEVELS
    Cads=0
    Cdfs=0
    Cdecomp=B(-:-:-)
    Creversible=yes
    Ckernels=W5X3
    Catk=0
    Cuse_precincts=yes
    Cprecincts={256,256},{256,256},{128,128},{128,128},{128,128},{128,128},{128,128}
    Cblk={64,64}
    Cmodes=0
    Qguard=1
    Qabs_ranges=4,5,5,6,5,5,6,5,5,6,5,5,6,5,5,5,4,4,5
    
    """
    if output_directory is None:
        output_directory = os.getcwd()
    if output_file is None:
        output_file = 'jp2.txt'
    
    
    if os.path.dirname(os.path.normpath(file_name)) != '':
        print 'Path: ' + os.path.dirname(os.path.normpath(file_name))
        input_file = os.path.normpath(file_name)
    else:
        input_file = path_file_combine(os.getcwd(),file_name)
    
    print 'Input file: ' + input_file     
       
    output_file_path = path_file_combine(output_directory,output_file)
    if (os.access(input_file,os.R_OK)) and (os.access(output_directory,os.W_OK)):## check file exists and output file writeable
            action = '/opt/kakadu/kdu_expand -i ' + input_file + ' -record ' + output_file_path
            p = subprocess.Popen(action, shell=True, stdout=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                print "Jpeg2000 data extraction failed \n"
            else:
                with open(output_file_path) as f:
                    jpeg2000_data = {'filename': input_file}
                    for line in f:
                        if (line[:1] is 'S') or (line[:1] is 'Q') or (line[:1] is 'C'):
                            details = line.split('=',1)
                            jpeg2000_data[details[0]]= details[1].strip()
                    return jpeg2000_data       
                os.unlink(output_file_path)
