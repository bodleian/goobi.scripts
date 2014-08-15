#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	ExportPath property insert

	Inserts exportpath property into goobi so that later scripts can use it

	Command line:
		needs: process_id, property_name and property_value

	Relies on steps:
		None

	Example run :
		In Goobi:
			/gscripts/bdlss/step_goobi_property_insert_exportpath.py process_id={processid} property_name=exportpath property_value=/opt/digiverso/export
		From command line:
			sudo -u tomcat6 /gscripts/bdlss/step_goobi_property_insert_exportpath.py process_id=200 property_name=exportpath property_value=/opt/digiverso/export

'''

from goobi.goobi_step import Step
from goobi.goobi_communicate import GoobiCommunicate

class Step_Goobi_Property_Insert_Exportpath( Step ) :

	def setup( s ):

		s.name = "Generic Property Insert"

		s.config_main_section = "property_inserter_exportpath"
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {
			# Use with self.command_line.NAME
			"process_id":Step.type_number,
			"property_name" : Step.type_string,
			"property_value" : Step.type_folder
		}

	def step( s ):

		"""
			Get settings and call communicate
		"""

		error = None

		goobi_com = GoobiCommunicate( s.config.goobi.host, s.config.goobi.passcode, s.debug )
		if not goobi_com.addProperty( s.command_line.process_id, s.command_line.property_name, s.command_line.property_value ) :
			error = "Failed to add exportpath property"

		return error




if __name__ == '__main__' :

	import config_ini
	Step_Goobi_Property_Insert_Exportpath( config_ini.file ).begin()









