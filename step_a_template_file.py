#!/usr/bin/python
# -*- coding: utf-8 -*-


from goobi.goobi_step import Step

class Step_${Step_Name} ( Step ) :

	'''
		${Step_Name}

		By ${USER} 
		${DATE}

		WHAT IT DOES!

		Command line:
			needs: process_id,  and WHAT IT NEEDS

		Relies on steps:
			DOES IT?

		Example run :
			In Goobi:
				/gscripts/bdlss/step_DUMMY.py process_id={processid} SOMETHING_HERE
			From command line:
				sudo -u tomcat6 ./step_DUMMY.py process_id=75 SOMETHING_HERE

	'''

	def setup( s ):
	
		s.name = "${Step_Name}"
		
		s.config_main_section = "CONFIG_SECTION!"
		s.essential_config_sections = {}
		s.essential_commandlines = {
			# Use with self.command_line.NAME
			"process_id":Step.type_number,
			# ANYTHING_ELSE?
		}
	
	def step( s ):
	
		"""
			How's it do it?
			
			Try using, debug, auto_complete, detach and report_problem on commandline
		"""
	
		error = None
		
		# DO SOMETHING...
		
		return error

		
		
		
if __name__ == '__main__' :

	import config_ini
	Step_${Step_Name}( config_ini.file ).begin()









