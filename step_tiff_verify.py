#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Tiff Verification
	
	Verify the TIFF files we passed into Goobi are valid 
	
	Command line:
		needs: process_id,  and tiff_folder
		optional: auto_complete, step_id, correction_step_name
		
	Relies on steps:
		none
	
	Example run : 
		In Goobi:  
			/opt/digiverso/goobi/scripts/bdlss/step_tiff_verify.py process_id={processid} original_tiff_path={origpath}
		From command line:
			sudo -u tomcat6 ./step_tiff_verify.py process_id=75 original_tiff_path=/opt/digiverso/goobi/metadata/75/images/master_healedanw_222_FFFFF_tif debug=True

'''

from goobi.goobi_step import Step
from jhove.jhove import Jhove

class Step_Tiff_Verify(Step):

	def setup( s ):
	
		s.name = "Tiff Verify"
	
		s.config_main_section = "tiff_verify" # Info for this particular step
		s.essential_config_sections = set( ['jhove'] )
		s.essential_commandlines = {
			"process_id":"number", 
			"original_tiff_path":"folder"
		}
	
	def step( self ):
	
		error = None
	
		jhove = Jhove( self.config.jhove.file, self.config.jhove.conf )
		
		details = jhove.checkFolder( self.command_line.original_tiff_path, Jhove.FILETYPE.TIFF )
		
		tiffs_failed = []
		for tiff_file in details:
			if not details[tiff_file]['ok']:
				tiffs_failed.append( tiff_file )
		
		if tiffs_failed:
			# Create error message
			error = "There was a problem with " + str( len( tiffs_failed ) ) + " tiff files. Details follow. \n"
			
			for tiff in tiffs_failed:
				error += 'Tiff "' + tiff + '" failed'
				error += ", " + details[tiff]['status']
				
				messages = []
				for message in details[tiff]['messages'] :
					messages.append( '"' +  message + '"' )
				
				if messages:
					error += " - " + ", ".join( messages )
				
				error += "\n"
				
			# self.error( error )
		
		return error


if __name__ == '__main__' :

	import config_ini
	Step_Tiff_Verify( config_ini.file ).begin( )






