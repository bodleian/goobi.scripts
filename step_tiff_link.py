#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Tiff folder symlink

	Symlink the original tiffs to the "working" folders.

	Command line:
		needs: process_id,  and WHAT IT NEEDS

	Relies on steps:
		DOES IT?

	Example run :
		In Goobi:
			/opt/digiverso/goobi/scripts/bdlss/step_tiff_link.py process_id={processid} original_path=... tiff_path=... 
		From command line:
			sudo -u tomcat6 ./step_tiff_link.py process_id=75  original_path=... tiff_path=...

'''

import os, os.path

from goobi.goobi_step import Step

class Step_Tiff_Link( Step ) :

	def setup( s ):

		s.name = "Tiff Link"

		s.config_main_section = "tiff_link"
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {
			"process_id": Step.type_number,
		    "original_path" : Step.type_folder,
			"tiff_path" :  Step.type_ignore
		}

	def step( s ):

		"""
			Symlink the original tiffs to a new folder.

			Report if we can't edit it.
		"""

		error = None


		if os.path.exists( s.command_line.tiff_path ) :

			if os.path.islink( s.command_line.tiff_path ) :

				try:
					# This isn't actually needed as (assuming the link points to the same place) we are just recreating the same thing later!
					os.remove( s.command_line.tiff_path )

				except OSError, e:
					error = "tiff_path (%s) already exists but I could not delete it." % s.command_line.tiff_path

			else:
				# I don't want to delete a folder of stuff.
				error = "tiff_path (%s) exists but it is not a symbolic link. I'm not deleting it!" % s.command_line.tiff_path


		if error is None:

			try:
				os.symlink( s.command_line.original_path, s.command_line.tiff_path )

			except OSError, e :
				error = "Exception creating symbolic link (%s to %s) - %s" % ( s.command_line.original_path, s.command_line.tiff_path, e )


		return error



if __name__ == '__main__' :

	import config_ini
	Step_Tiff_Link( config_ini.file ).begin()










