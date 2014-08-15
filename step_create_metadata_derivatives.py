#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Generate derivative metadata

	Create and verify the jpeg2000 derivitives.

	Command line:
		needs: process_id,  and tiff_folder
		optional: auto_complete, step_id, correction_step_name

	Relies on steps:
		Update METS URIs step. (step_mets_uri_update.py)

	Example run :
		In Goobi:
			/opt/digiverso/goobi/scripts/bdlss/step_create_metadata_derivatives.py process_id={processid} export_folder=/opt/digiverso/export/{processtitle}/ exported_mets_file=/opt/digiverso/export/{processtitle}/{processtitle}.xml
		From command line:
			sudo -u tomcat6 python step_create_metadata_derivatives.py process_id=54 exported_mets_file=/opt/digiverso/export/_7654321/_7654321.xml export_folder=/opt/digiverso/export/_7654321/
'''

# example run :
## In Goobi:  /usr/bin/python /opt/digiverso/goobi/scripts/databank/step_metadata.py process_id={process_id} tiff_folder={tifpath}
## From command line: sudo -u tomcat6 python step_jpeg2000_create.py process_id=54 tiff_folder=/opt/digiverso/goobi/metadata/54/images/_7654321_tif

import os.path

from goobi.goobi_step import Step
from xxml.xslt import XSLT

class Step_Create_Metadata_Derivatives( Step ) :

	def setup( s ):

		s.name = "Create Metadata Derivatives"

		s.config_main_section = "derivative_metadata"
		s.essential_config_sections = { "saxon" }
		s.essential_commandlines = {
			"process_id" :				Step.type_number,
			"exported_mets_file" :	Step.type_file, # File to generate from (this should already have updated (databank) URIs in from a previous step.
			"export_folder"	: 			Step.type_folder # Where to create derivatives.
		}

	def step( self ) :

		"""
			Create a derivative DC format of the METS file.

			Files are placed in a sub directory, the names consist of the ID of the image they are based on (This is extracted from the METS)
		"""
		error = None

		x = XSLT( self.config.saxon.file, self.glogger )

		# Generate DC
		dc_generate = os.path.join( self.config.derivative_metadata.xsl_folder, self.config.derivative_metadata.dc_stylesheet )
		dc_output = os.path.join( self.command_line.export_folder, "dc/" )

		success = x.generate( self.command_line.exported_mets_file, dc_generate, params={"outputDir": dc_output } )

		if not success:
			error = 'There was a problem converting to DC.'

		return error




if __name__ == '__main__' :

	import config_ini
	Step_Create_Metadata_Derivatives( config_ini.file ).begin( )









