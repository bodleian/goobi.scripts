#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path
from lxml import etree

from goobi.goobi_step import Step
from exempi.exempi import Exempi

class Step_Extract_XMP( Step ) :

	'''
		Extract XMP data step

		It extracts the XMP data embedded in a file format into a new file.

		Command line:
			needs: process_id,  and WHAT IT NEEDS

		Relies on steps:
			DOES IT?

		Example run :
			In Goobi:
				/gscripts/bdlss/step_extract_xmp.py process_id={processid} tiff_path={tifpath} export_folder={process.exportpath}/{processtitle}/ exported_mets_file={process.exportpath}/{processtitle}/{processtitle}.xml detach=True auto_complete=True
			From command line:
				sudo -u tomcat6 ./step_extract_xmp.py process_id=215 tiff_path=/opt/digiverso/goobi/metadata/215/images/Holkd32_014503749_tif exported_mets_file=/opt/digiverso/export/Holkd32_014503749/Holkd32_014503749.xml

	'''

	def setup( s ):

		s.name = "Extract XMP"

		s.config_main_section = "extract_xmp"
		s.essential_config_sections = { "exempi" }
		s.essential_commandlines = {
			# Use with self.command_line.NAME
			"process_id": Step.type_number,
			"tiff_path":  Step.type_folder,
		    "export_folder" : Step.type_folder,
		    "exported_mets_file" : Step.type_file
		}

	def step( s ):

		"""
			How's it do it?

			Try using, debug, auto_complete, detach and report_problem on commandline
		"""
		error = None

		mets_file = s.command_line.exported_mets_file
		mets_file_original = mets_file + s.config.general.mets_file_original_extension

		# If we have the original file use it, otherwise it's already the original (i.e. unchanged) file.
		if s.checkFile( mets_file_original ) is None :
			mets_file = mets_file_original

		mets, error = s._open( mets_file )

		if mets is not None :

			# Get file list and uuids
			filenames = {}

			schema = r"{http://www.loc.gov/METS/}"

			root = mets.getroot()

			for div_element in root.iterfind( r"./{0}structMap[@TYPE='PHYSICAL']/{0}div/{0}div".format (schema) ) :

				uuid = div_element.get( "CONTENTIDS" )[9:]

				fptr = div_element.find( "{0}fptr[1]".format(schema) )

				xpath = r"./{0}fileSec/{0}fileGrp/{0}file[@ID='{1}']/{0}FLocat".format( schema, fptr.get( "FILEID" ) )

				file_link = root.find( xpath )

				file_href_name = os.path.basename( file_link.get( "{http://www.w3.org/1999/xlink}href" ) )
				file_href_basename = file_href_name[:file_href_name.find(".")]

				filenames[file_href_basename] = uuid

				#print filenames

			if len( filenames ) > 0:

				ex = Exempi( s.config.exempi.file, s.glogger )

				save_folder = os.path.join( s.command_line.export_folder, "xmp" )
				if not os.path.exists( save_folder ) :
					os.makedirs( save_folder )

				for filename in filenames :

					# Get tiff position

					tiff_position = os.path.join( s.command_line.tiff_path, filename + ".tif" )

					if s.checkFile( tiff_position ) is not None:
						tiff_position += "f"
						if s.checkFile( tiff_position ) is not None :
							tiff_position = None


					if tiff_position is None:
						s.warning_message( "Can't file tiff file starting with " + filename + " in " + s.command_line.tiff_path )
						print "Missing " + filename + " in " + s.command_line.tiff_path
					else :

						print "Found Tiff "

						uuid = filenames[filename]

						# Extract tiff info
						ex.generate( tiff_position, os.path.join(save_folder,"xmp_" + uuid + ".xml") )

		else :

			error = "Unable to open METS file"





		return error












	def _open( self, file ):
		""" Open a file and pass it into the tree parser """
		try:
			xml = etree.parse( file )
		except IOError:
			return None, "Failed to open file: " + file
		except etree.XMLSyntaxError as ex:
			return None, "XML syntax error: " + file + " - " + ex.msg

		return xml, ''


if __name__ == '__main__' :

	import config_ini
	Step_Extract_XMP( config_ini.file ).begin()










