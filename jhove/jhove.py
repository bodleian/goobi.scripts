#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, commands
from lxml import etree

class Jhove(object):

	"""
		Using jhove to check TIFFS (and other file types)
		
		Downloaded jhove 1.11 from http://downloads.sourceforge.net/project/jhove/jhove/JHOVE%201.11/jhove-1_11.zip?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fjhove%2Ffiles%2Fjhove%2F&ts=1386784000&use_mirror=kent
		Following instructions at http://jhove.sourceforge.net/using.html
	"""

	audit_valid = "valid"
	file_valid = "Well-Formed and valid"
	
	debug = False
	
	class FILETYPE:
	
		AIFF = 1
		ASCII = 2
		GIF = 3
		HTML = 4
		JPEG = 5
		JPEG2000 = 6
		PDF = 7
		TIFF = 8
		UTF8 = 9
		WAVE = 10
		XML = 11
		
		MODULE = {
			AIFF : "AIFF-hul",
			ASCII : "ASCII-hul",
			GIF : "GIF-hul",
			HTML : "HTML-hul",
			JPEG : "JPEG-hul",
			JPEG2000 : "JPEG2000-hul",
			PDF : "PDF-hul",
			TIFF : "TIFF-hul",
			UTF8 : "UTF8-hul",
			WAVE : "WAVE-hul",
			XML : "XML-hul"
		}
		
		EXTENSIONS = {
			AIFF : ['aiff'],
			ASCII : [],
			GIF : ['gif'],
			HTML : ['htm','html'],
			JPEG : ['jpg','jpeg'],
			JPEG2000 : ['jpg2','jp2'],
			PDF : ["pdf"],
			TIFF : ['tif','tiff'],
			UTF8 : [],
			WAVE : ['wav'],
			XML : ['xml','rtf','xsl']
		}
	
	def __init__( self, jhove_app, jhove_conf, logger=None ) :
	
		self.jhove = jhove_app
		self.jhove_conf = jhove_conf
		
		self.logger = logger
		
	def auditFolder( self, folder, mimetype=None ) :
		"""
			This actually detects what files ARE, not what they SHOULD BE.
			
			For instance an invalid tiff file will be marked as a binary file ( because it doesn't match anything specific... )
		"""
		errors = []
		
		if not os.path.exists( self.jhove ) :
			self._error( "Jhove: jhove not found at \"" + self.jhove + "\"" )
			return False
			
		if not os.path.exists( self.jhove_conf ) :
			self._error( "Jhove: Configuration file not found at \"" +  self.jhove_conf  + "\"" )
			return False
			
		if not os.path.isdir( folder ) :
			self._error( "Jhove: Folder to check not found \"" + folder + "\"" )
			return False
		
		command = self._default_command_audit()
		command += " " + folder
		
		# <?xml version="1.0" encoding="UTF-8"?>\n<jhove xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://hul.harvard.edu/ois/xml/ns/jhove" xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/jhove http://hul.harvard.edu/ois/xml/xsd/jhove/1.6/jhove.xsd" name="Jhove" release="1.11" date="2013-09-29">\n <date>2013-12-13T18:16:21+00:00</date>\n <audit home="/home/goobiadmin/subversion/digitisationfoundation/trunk/digiverso/goobi/scripts/bdlss/jhove">\n  <file mime="image/jp2" status="valid">/opt/digiverso/goobi/metadata/36/images/master_apiTest4_tif/KENNICOTT_BIBLE_000_b.jp2</file>\n  <file mime="image/tiff" status="valid">/opt/digiverso/goobi/metadata/36/images/master_apiTest4_tif/KENNICOTT_BIBLE_000_b.tif</file>\n </audit>\n</jhove>\n<!-- Summary by MIME type:\nimage/jp2: 1 (1,0)\nimage/tiff: 1 (1,0)\nTotal: 2 (2,0)\n-->\n<!-- Summary by directory:\n/opt/digiverso/goobi/metadata/36/images/master_apiTest4_tif: 2 (2,0) + 0,0\nTotal: 2 (2,0) + 0,0\n-->\n<!-- Elapsed time: 0:00:01 -->
		jhove_returned = commands.getstatusoutput( command )
		
		# print jhove_returned[1]
		root = etree.fromstring( jhove_returned[1] )

		jhove_files = root.findall( ".//{http://hul.harvard.edu/ois/xml/ns/jhove}file" )
		
		#  <file mime="image/tiff" status="valid">/opt/digiverso/goobi/metadata/101/images/master_carralic22_tif/axc0015-0.tif</file>
		error_files = []
		for jhove_file in jhove_files :
		
			if mimetype == None or minetype == hove_file.get("mime") :
				if jhove_file.get("status") != Jhove.audit_valid:
					error_files.append( jhove_file.text )
		
		return error_files

	def checkFolder( self, folder, filetype, exts=None ):
	
		if not exts :
			exts = self._getExtensions( filetype )
			
			if not exts:
				# TODO raise parameter exception
				# Some types have no extensions set...
				return None
	
		files = []
		for file in os.listdir( folder ):
			for ext in exts:
				if file.endswith( "." + ext ):
					files.append( os.path.join( folder,file ) )
					break
					
		return self.checkFiles( files, filetype )
	
	
	def checkFiles( self, files, filetype ):
		""" 
			Take a list of tiffs and return if they are valid.
			
			Return in form of 
				{ 'FILENAME' : { 'ok' : BOOLEAN, 'status' : STATUS, 'messages' : [MESSAGE,MESSAGE] } }
			e.g. :
				{ '/opt/digiverso/goobi/metadata/81/images/QA_jpegs/00000002.jpg': {'ok':False, 'status': 'Not well-formed', 'messages': ['No TIFF header: ']}
		"""
		
		stati = {}
		if files:
		
			command = self._default_command_file_details( filetype )
			command += " ".join( files )
			
			if self.debug:
				print command
			
			# <?xml version="1.0" encoding="UTF-8"?><jhove xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://hul.harvard.edu/ois/xml/ns/jhove" xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/jhove http://hul.harvard.edu/ois/xml/xsd/jhove/1.6/jhove.xsd" name="Jhove" release="1.11" date="2013-09-29"><date>2013-12-12T11:14:48+00:00</date><repInfo uri="/opt/digiverso/goobi/metadata/101/images/carralic22_jpg/axc0015-0.jpg"><reportingModule release="1.7" date="2012-08-12">TIFF-hul</reportingModule><lastModified>2013-07-22T15:40:59+01:00</lastModified><size>1391446</size><format>TIFF</format><status>Not well-formed</status><messages><message offset="0" severity="error">No TIFF header: ￿￘</message></messages> <mimeType>image/tiff</mimeType></repInfo>
			jhove_returned = commands.getstatusoutput( command )
			
			# There are invalid characters (even for UTF-8) which need to be removed (can you believe they output the TIFF FILEIDs into the XML if it isn't found!)
			def unicode_filter(char):
				try:
					unicode( char, encoding='utf-8', errors='strict' )
					return char
				except UnicodeDecodeError:
					return ''

				#test
				#content = 'abc\xFF'
				#content = ''.join(map(unicode_filter, content))
			
			
			root = etree.fromstring( ''.join(map(unicode_filter, jhove_returned[1])) )

			jhove_infos = root.findall( ".//{http://hul.harvard.edu/ois/xml/ns/jhove}repInfo" )
			
			for jhove_info in jhove_infos:
			
				file = jhove_info.get( "uri" )
				
				# SHould always be a status
				status = jhove_info.find( "{http://hul.harvard.edu/ois/xml/ns/jhove}status" ).text
				# There may be errors (as messages)
				message_nodes = jhove_info.findall( "{http://hul.harvard.edu/ois/xml/ns/jhove}messages/{http://hul.harvard.edu/ois/xml/ns/jhove}message" )
				
				messages = []
				for message in message_nodes:
					messages.append( message.text )
				
				stati[file] = { "status" : status, "ok" : (status == Jhove.file_valid) }
				if messages:
					stati[file]["messages"] = messages
		
		return stati
		
	def _getModule( self, filetype ):
	
		return Jhove.FILETYPE.MODULE[filetype]
		
	def _getExtensions( self, filetype ):
	
		return Jhove.FILETYPE.EXTENSIONS[filetype]
		
	def _default_command( self ):
		#./jhove -l OFF -c ./conf/jhove.conf # Turn logging off and pass in configuration file.
		command = self.jhove + " -l OFF -e utf8 -c " + self.jhove_conf 
		return command
	
	
	def _default_command_audit( self ):
		# ./jhove -c ./conf/jhove.conf -h audit /opt/digiverso/goobi/metadata/101/images/carralic22_tif/
		command = self._default_command()
		command += " -h audit "
		return command
		
	def _default_command_file_details( self, filetype ):
		# ./jhove -c ./conf/jhove.conf -m FILEYTPEMODULE -h xml /opt/digiverso/goobi/metadata/101/images/carralic22_jpg/

		module = self._getModule( filetype )

		command = self._default_command()
		command += " -m " + module + " -h xml "	
		return command
		
	def _error( self, message ):
		if self.logger:
			self.logger.error( self._wrap_message(message) )
		if self.debug :
			print "Error:" + message
			
	def _warning( self, message ):
		if self.logger:
			self.logger.warning( self._wrap_message(message) )
	def _info( self, message ):
		if self.logger:
			self.logger.info( self._wrap_message(message) )
	def _debug( self, message ):
		if self.logger:
			self.logger.debug( self._wrap_message(message) )
			
			
if __name__ == '__main__' :
	
	# Run a quick test
	jhove = Jhove( "/opt/jhove/jhove", "/opt/jhove/conf/jhove.conf" )
	

	# A tiff folder
	error_tiffs = None
	
	#error_tiffs = jhove.auditFolder( "/opt/digiverso/goobi/metadata/36/images/master_apiTest4_tif/" )
	error_tiffs = jhove.auditFolder( "/opt/digiverso/goobi/scripts/bdlss/jhove/sample_test_tiffs" )

	if error_tiffs :
		print "Some errors in folders with: " + str( error_tiffs )
	else:
		print "No errors in folder"

	
	# Check Jpegs are tiffs...
	print "Check Jpegs are TIFFS:\n", jhove.checkFiles( [
		"/opt/digiverso/goobi/metadata/54/images/_7654321_jpg/MS_HEB_c_9_1a.jpg",
		"/opt/digiverso/goobi/metadata/54/images/_7654321_jpg/MS_HEB_c_9_1b.jpg"
	], Jhove.FILETYPE.TIFF )
	
	
	#Check Jpegs are Jpegs
	print  "Check Jpegs are JPEGS:\n", jhove.checkFiles( [
		"/opt/digiverso/goobi/metadata/54/images/_7654321_jpg/MS_HEB_c_9_1a.jpg",
		"/opt/digiverso/goobi/metadata/54/images/_7654321_jpg/MS_HEB_c_9_1b.jpg"
	], Jhove.FILETYPE.JPEG )
	

	# Check a folder with TIFF's in.
	print "Check a folder with tiffs in:\n", jhove.checkFolder( "/opt/digiverso/goobi/scripts/bdlss/jhove/sample_test_tiffs", Jhove.FILETYPE.TIFF )
	
	