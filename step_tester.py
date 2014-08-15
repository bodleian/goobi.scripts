#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Tester
	
	Test the python step code.
	
	Command line:
		needs: process_id,  and tiff_folder
		optional: auto_complete, step_id, correction_step_name
	
	Relies on steps:
		none
	
	Example run : 
		In Goobi:  
			/usr/bin/python /opt/digiverso/goobi/scripts/bdlss/step_tester.py process_id={processid} tiff_folder={tifpath}
		From command line:
			sudo -u tomcat6 python step_tester.py process_id=54 tiff_folder=/opt/digiverso/goobi/metadata/54/images/_7654321_tif

'''

from goobi.goobi_step import Step

class Step_Tester( Step ) :

	def setup( s ):
	
		s.name = "Test-a-step"
		
		s.config_main_section = "step_tester"
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {
			"process_id":"number", 
			"tiff_path":"folder"
		}
	
	def step( s ):
	
		"""
			This just tests the step code
			
			Try using, debug, auto_complete, detach and report_problem on commandline
		"""
	
		error = None
		
		s.debug_message( "I'm some debug in Step_Tester" )
		s.info_message( "I'm some info in Step_Tester" )
		s.warning_message( "I'm some warning in Step_Tester" )
		
		print "Doing nothing. Except printing this..."
		
		if s.command_line.has( "create_error" ) :
		
			print "Pretending something has gone wrong..."
			error = "I'm some error in Step_Tester"
		
		if s.detach :
			
			# pretend we are doing something that takes a long time
			import time
			time.sleep( 5 )
			
			s.info_message( "Completed something that took 15 seconds." )
			s.warning_message( "Let's pretend there's a warning here." )
		
		return error

		
		
		
if __name__ == '__main__' :

	import config_ini
	Step_Tester( config_ini.file ).begin()









