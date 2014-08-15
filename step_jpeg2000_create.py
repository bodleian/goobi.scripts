#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Jpeg2000 Create
	
	Takes existing TIFFS and creates JPEG2000 files from them
	
	Command line:
		needs: process_id,  and tiff_path
	
	Relies on steps:
		None
	
	Example run : 
		In Goobi:  
			/gscripts/bdlss/step_jpeg2000_create.py process_id={processid} tiff_path={tifpath} detach=True auto_complete=True
		From command line:
			sudo -u tomcat6 ./step_jpeg_create.py process_id=75 tiff_path=/opt/digiverso/goobi/metadata/75/images/healedanw_222_FFFFF_tif

'''

import os, os.path, shutil

from image_processing import fnmatch, check_corresponding_file, compress_jp2_colour
from goobi.goobi_step import Step

class Step_Jpeg2000_Create( Step ) :

	def setup( s ):
	
		s.name = "Jpeg2000 Create"
		
		s.config_main_section = "jpeg2000_create"
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {
			"process_id":	Step.type_number, 
			"tiff_path" :  Step.type_folder
		}
	
	def step( s ):
	
		"""
			Uses image_processing python file to create (code from jpeg_convert)
			
			Try using, debug, auto_complete, detach and report_problem on commandline
		"""
	
		error = None

		
		jp2_path = s.command_line.tiff_path.replace( '_tif', '_jp2' )


		if os.path.isdir( jp2_path ) : ## check if directory already exist
			shutil.rmtree( jp2_path )
			
		os.makedirs(jp2_path) # make full path
		
		masterworkingdir = os.path.normpath(s.command_line.tiff_path)
		
		
		def print_fnmatches(pattern, dir, files):
			for filename in files:
				if fnmatch(filename, pattern):
					tiff_list.append( os.path.join(dir, filename) )
 
 
		tiff_list=[]
		os.path.walk(masterworkingdir, print_fnmatches, '*.tif')

		s.debug_message( 'Walking over: ' + masterworkingdir )
		
		
		for file in tiff_list:
			if check_corresponding_file( file ) is False:
				compress_jp2_colour( file, masterworkingdir,jp2_path )
		
		
		return error

		
		
		
if __name__ == '__main__' :

	import config_ini
	Step_Jpeg2000_Create( config_ini.file ).begin()









