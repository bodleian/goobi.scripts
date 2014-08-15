#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Jpeg2000 Verification
	
	Verify the JPEG2000 files we created from tiff files are valid 
	
	Command line:
		needs: process_id,  and tifffolder
		optional: auto_complete, step_id, correction_step_name
		
	Relies on steps:
		none
	
	Example run : 
		In Goobi:  
			/opt/digiverso/goobi/scripts/bdlss/step_jperg_verify.py process_id={processid} tiff_path={tifpath}
		From command line:
			sudo -u tomcat6 ./step_jpeg2000_verify.py process_id=75 tiff_path=/opt/digiverso/goobi/metadata/75/images/healedanw_222_FFFFF_tif debug=True

'''

from goobi.goobi_step import Step
from jhove.jhove import Jhove

class Step_Jpeg2000_Verify(Step):

	def setup( s ):
	
		s.name = "JPEG2000 Verify"
	
		s.config_main_section = "jpeg2000_verify" # Info for this particular step
		s.essential_config_sections = set( ['jhove'] )
		s.essential_commandlines = {
			"process_id":"number", 
			"tiff_path":"folder"
		}
	
	def step( self ):
	
		error = None
	
		# Get jpeg path and check
		jpeg_path = self.command_line.tiff_path.replace( '_tif', '_jp2' )
	
		if self.checkFolder( jpeg_path ) == None :
		
			jhove = Jhove( self.config.jhove.file, self.config.jhove.conf )
			details = jhove.checkFolder( jpeg_path, Jhove.FILETYPE.JPEG2000 )
			
			files_failed = []
			for file in details:
				if not details[file]['ok']:
					files_failed.append( file )
			
			if files_failed:
				# Create error message
				error = "There was a problem with " + str( len( files_failed ) ) + " jpeg2000 files. Details follow. \n"
				
				for file in files_failed:
					error += 'Jpeg2000 "' + file + '" failed'
					error += ", " + details[file]['status']
					
					messages = []
					for message in details[file]['messages'] :
						messages.append( '"' +  message + '"' )
					
					if messages:
						error += " - " + ", ".join( messages )
					
					error += "\n"
					
				# self.error( error )
		
		else:
			error = "Jpeg2000 folder " + jpeg_path + " does not exist"
		
		return error


if __name__ == '__main__' :

	import config_ini
	Step_Jpeg2000_Verify( config_ini.file ).begin( )






