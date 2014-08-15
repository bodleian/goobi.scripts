# -*- coding: utf-8 -*-

import sys, os, os.path, re, traceback, datetime, subprocess
import logging, logging.handlers

from abc import abstractmethod, ABCMeta

from config.config_reader import ConfigReader
from cli.command_line import CommandLine
from goobi.goobi_communicate import GoobiCommunicate
from goobi.goobi_logger import GoobiLogger

		
class Step( object ):
	"""
		Base class for all steps.
		
		This :
			Checks config
			Checks commandline 
			Creates loggers - goobi, file and email.
			
		Additional commandlines:
			detach - if true the step will detach from goobi after the basic checks are done, the file continues to be run but Goobi no longer watches it or moves to another step.
			auto_complete - if true and the step completes fine, the step will be closed.
			auto_report_problem - auto return to another step if this step fails. Equal to the stepname (step_id={stepid} is also needed to report to a previous step)
			debug - override config debug value to display additional information and output more information.
		
		First define the setup(s) function.
			give the step a name, 
			s.name="my step name"
		Then specify the default config section for this step, 
			s.config_main_section='uuid_insert'
		Then specify the set of essential config sections this step needs to run, 
			s.essential_config_sections=set( ["sec1","sec2"] )
		Then specify the dict of essential commandlin values with a type (number, file, folder or string), 
			s.essential_commandlines = { "process_id" : "number", "metafile" : "file", "tiff_path" : "folder", "step_name" : "string" }
			
		Now put your code in the step() function. 
			You can acess self.commandline and self.config. 
			Use error(), warning(), info() and debug() to log to the logger.
		
		You can use other commandline parameters for the process id and step id by overwriting commandline_process_id and commandline_step_id in the child class
	"""
	
	# Types for commandlines
	type_string = "string"
	type_number = "number"
	type_file = "file"
	type_folder = "folder"
	type_ignore = "ignore"
	
	# TODO: Switch types to these: (Use with Step.CLTYPE.STRING
	class CLTYPE:
		STRING = "string"
		NUMBER = "number"
		FILE = "file"
		FOLDER = "folder"
		IGNORE = "ignore"

	
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def setup(_): pass
	
	@abstractmethod
	def step(_): pass

	# TODO? @abstractmethod def teardown(_):pass
	
		
	def __init__( s, config_file ) :
	
		# Default names for essential settings
		s.commandline_process_id = "process_id"
		s.commandline_step_id = "step_id"
		s.commandline_auto_report_problem_step_name = "auto_report_problem"
		s.config_general_section = "general"
		
		
		s.name = ""
		
		s.config_main_section = "" # Info for this particular step
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {}

		s.command_line = None
		s.config = None
		
		s.glogger = None
		s.glogger_handlers = {}
		
		s.debug = False
		s.auto_complete = False
		s.detach = False
		s.only_file_log = False
		
		
		s.setup()
		
		
		# Create list of config setions we want. Always assume Goobi is needed.
		s.essential_config_sections.update( ["goobi", s.config_main_section] ) 
		
		# Add process_id to default commandlines - we need it for logging to Goobi
		if s.commandline_process_id not in s.essential_commandlines.keys() :
			s.essential_commandlines[s.commandline_process_id] = "number"
		
		#
		# Get configuration information
		#
		s.config, error = s.getConfig( config_file, must_have=s.essential_config_sections )
		if error:
			s.exit( None, error )
		
		
		#
		# Get command line parameters (want to pass process_id to log if we have it)
		#
		s.command_line, error_command_line= s.getCommandLine( must_have=s.essential_commandlines )
		
		#
		# Are we debugging?
		#
		s.debug = s.debugging( s.config )
			
		if s.command_line and s.command_line.has( "debug" ) :
			s.debug = not ( s.command_line.debug.lower() == "false" ) # Override config setting at commandline. (if it says anything but false turn it on.)

			if s.command_line.has( "only_file_log" ) :
				s.only_file_log = s.command_line.only_file_log.lower() == "true"

		if s.debug:
			print s.name + ": Debugging ON"

		# 
		# Create out logger
		#
		s.glogger, error = s.getLoggingSystems( s.config, s.config_main_section, s.command_line, s.debug, s.name + "_logger", s.only_file_log )
		if error:
			s.exit( s.glogger, error )
		
		#
		# Check Commandline parameters
		#
		if error_command_line:
			s.exit( s.glogger, error_command_line )
			
		if s.command_line.has( "auto_complete" ) :
			s.auto_complete = ( s.command_line.auto_complete.lower() == "true" )

		if s.command_line.has( "detach" ) :
			s.detach = ( s.command_line.detach.lower() == "true" )
			
		s.auto_report_problem = s.command_line.has( s.commandline_auto_report_problem_step_name )
		
		
		#
		# Pass message back to Goobi to say everything looks fine and start process.
		#
		update_message = "Basic checks complete, "
		update_message += 'beginning main process of step "' + s.name + '" - '
		update_message += 'DETACH:' + ( "ON" if s.detach else "OFF" )
		update_message += ', AUTO-COMPLETE:' + ( "ON" if s.auto_complete else "OFF" ) # if successful
		update_message += ', REPORT-PROBLEM:' + ( "ON" if s.auto_report_problem else "OFF" ) # if unsuccessful
		update_message += ', DEBUG:' + ( "ON" if s.debug else "OFF" ) + "."

		update_message += ' Commandline: ' + str(s.command_line)
		
		s.info_message( update_message )


	def begin(s) :
	
		if s.detach:
			
			# Detach from goobi.
			s.detachSelf()
			
			
		error = None
		
		try:
			error = s.step()
			
		except Exception, e:

			try:
				trace = traceback.format_exc()
				s.error_message( 'Exception occured in ' + s.name + ' :- ' + e.message + ". Trace: " + trace )
			except:
				s.error_message( 'Exception occured in ' + s.name  )
				
			raise
		
		if not error :
		
			s.info_message( 'Completed ' + s.name )

			if s.auto_complete:
				s.closeStep()

		else:
			
			s.error_message( 'Failed ' + s.name + ".  " + error )
			
			if s.auto_report_problem: # Auto report to previous step if needed
				s.reportToStep( error )
			
			
		return ( error == None )


	def detachSelf( s ):
		
		# Flush stdout
		sys.stdout.flush()
		
		# Push out error so that Goobi will pause the current step (if auto_complete was specified the step will continue when finished)
		#		
		sys.stderr.write( "Step is continuing in background. (This is not an error!).\n" )
		sys.stderr.flush()
		
		# Close log_handlers (The daemon closes all files, but the logger doesn't know it's been closed unless you tell it!)
		for log_handler in s.glogger_handlers :
			s.glogger_handlers[log_handler].close()
		
		# detach this process from whatever started it (probably Goobi, but could be a shell)
		s.createDaemon()
		

	def createDaemon( s ):
	
		"""
			Detach a process from the controlling terminal and run it in the background as a daemon.
			
			From: http://code.activestate.com/recipes/278731/
		"""
		
		# Default daemon parameters.
		# File mode creation mask of the daemon.
		UMASK = 0
		
		# Default working directory for the daemon.
		WORKDIR = "/"

		# Default maximum for the number of available file descriptors.
		MAXFD = 1024

		# The standard I/O file descriptors are redirected to /dev/null by default.
		if ( hasattr(os, "devnull") ):
		   REDIRECT_TO = os.devnull
		else:
		   REDIRECT_TO = "/dev/null"

		try:
			# Fork a child process so the parent can exit.  This returns control to
			# the command-line or shell.  It also guarantees that the child will not
			# be a process group leader, since the child receives a new process ID
			# and inherits the parent's process group ID.  This step is required
			# to insure that the next call to os.setsid is successful.
			pid = os.fork()
			
		except OSError, e:
			raise Exception, "%s [%d]" % (e.strerror, e.errno)

		if (pid == 0):	# The first child.
			# To become the session leader of this new session and the process group
			# leader of the new process group, we call os.setsid().  The process is
			# also guaranteed not to have a controlling terminal.
			os.setsid()

			# Is ignoring SIGHUP necessary?
			#
			# It's often suggested that the SIGHUP signal should be ignored before
			# the second fork to avoid premature termination of the process.  The
			# reason is that when the first child terminates, all processes, e.g.
			# the second child, in the orphaned group will be sent a SIGHUP.
			#
			# "However, as part of the session management system, there are exactly
			# two cases where SIGHUP is sent on the death of a process:
			#
			#   1) When the process that dies is the session leader of a session that
			#      is attached to a terminal device, SIGHUP is sent to all processes
			#      in the foreground process group of that terminal device.
			#   2) When the death of a process causes a process group to become
			#      orphaned, and one or more processes in the orphaned group are
			#      stopped, then SIGHUP and SIGCONT are sent to all members of the
			#      orphaned group." [2]
			#
			# The first case can be ignored since the child is guaranteed not to have
			# a controlling terminal.  The second case isn't so easy to dismiss.
			# The process group is orphaned when the first child terminates and
			# POSIX.1 requires that every STOPPED process in an orphaned process
			# group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
			# second child is not STOPPED though, we can safely forego ignoring the
			# SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
			#
			# import signal           # Set handlers for asynchronous events.
			# signal.signal(signal.SIGHUP, signal.SIG_IGN)

			try:
			   #	 Fork a second child and exit immediately to prevent zombies.  This
				# causes the second child process to be orphaned, making the init
				# process responsible for its cleanup.  And, since the first child is
				# a session leader without a controlling terminal, it's possible for
				# it to acquire one by opening a terminal in the future (System V-
				# based systems).  This second fork guarantees that the child is no
				# longer a session leader, preventing the daemon from ever acquiring
				# a controlling terminal.
				
				pid = os.fork()	# Fork a second child.
				
			except OSError, e:
				raise Exception, "%s [%d]" % (e.strerror, e.errno)

			if (pid == 0):	# The second child.
				# Since the current working directory may be a mounted filesystem, we
				# avoid the issue of not being able to unmount the filesystem at
				# shutdown time by changing it to the root directory.
				os.chdir(WORKDIR)
				# We probably don't want the file mode creation mask inherited from
				# the parent, so we give the child complete control over permissions.
				os.umask(UMASK)
			else:
				# exit() or _exit()?  See below.
				
				os._exit(0)	# Exit parent (the first child) of the second child.
		else:
		
			# exit() or _exit()?
			# _exit is like exit(), but it doesn't call any functions registered
			# with atexit (and on_exit) or any registered signal handlers.  It also
			# closes any open file descriptors.  Using exit() may cause all stdio
			# streams to be flushed twice and any temporary files may be unexpectedly
			# removed.  It's therefore recommended that child branches of a fork()
			# and the parent branch(es) of a daemon use _exit().
			
			os._exit(0)	# Exit parent of the first child.

		# Close all open file descriptors.  This prevents the child from keeping
		# open any file descriptors inherited from the parent.  There is a variety
		# of methods to accomplish this task.  Three are listed below.
		#
		# Try the system configuration variable, SC_OPEN_MAX, to obtain the maximum
		# number of open file descriptors to close.  If it doesn't exists, use
		# the default value (configurable).
		#
		# try:
		#    maxfd = os.sysconf("SC_OPEN_MAX")
		  # except (AttributeError, ValueError):
		#    maxfd = MAXFD
		#
		# OR
		#
		# if (os.sysconf_names.has_key("SC_OPEN_MAX")):
		#    maxfd = os.sysconf("SC_OPEN_MAX")
		# else:
		#    maxfd = MAXFD
		#
		# OR
		#
		# Use the getrlimit method to retrieve the maximum file descriptor number
		# that can be opened by this process.  If there is not limit on the
		# resource, use the default value.
		#
		import resource		# Resource usage information.
		maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
		if (maxfd == resource.RLIM_INFINITY):
			maxfd = MAXFD
	  
		# Iterate through and close all file descriptors.
		for fd in range(0, maxfd):
			try:
				os.close(fd)
			except OSError:	# ERROR, fd wasn't open to begin with (ignored)
				pass
		
		
		# Redirect the standard I/O file descriptors to the specified file.  Since
		# the daemon has no controlling terminal, most daemons redirect stdin,
		# stdout, and stderr to /dev/null.  This is done to prevent side-effects
		# from reads and writes to the standard I/O file descriptors.

		# This call to open is guaranteed to return the lowest file descriptor,
		# which will be 0 (stdin), since it was closed above.
		#
		os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)
		
		return(0)
	
	
	def reportToStep( s, message ):
		"""
			Pass control back to a previous step
		"""
		
		if s.auto_report_problem:
		
		
			if s.command_line.has( s.commandline_step_id ) :
				s.info( 'Reporting this problem to  "' + s.command_line.get(s.commandline_auto_report_problem_step_name) + "\" step." )
				goobi_com = GoobiCommunicate( s.config.goobi.host, s.config.goobi.passcode, s.debug )
				goobi_com.reportProblem( s.command_line.get( s.commandline_step_id ), s.command_line.get(s.commandline_auto_report_problem_step_name), message )
			else :
				s.info( 'Failed to report this problem to a previous step. In ' + s.name + " " + s.commandline_step_id + " was not passed into commandline." )
		
		
		
	def closeStep( s ):
	
		goobi_com = GoobiCommunicate( s.config.goobi.host, s.config.goobi.passcode, s.debug )
		
		if s.command_line.has( s.commandline_process_id ) :
			goobi_com.closeStepByProcessId( s.command_line.get( s.commandline_process_id ) )
		elif s.command_line.has( s.commandline_step_id ) :
			goobi_com.closeStep( s.command_line.get( s.commandline_step_id ) )
		else:
			s.info( 'Failed to close this step in ' + s.name + ". Neither " + s.commandline_process_id + " or " + s.commandline_step_id + " were passed into commandline." )
			

	def exit( self, log, message ) :
		''' Nice exit '''

		if log:
			log.error( message )

		print "Exit message: " + str( message )

		sys.exit(1)
		
	def getConfig( self, file, must_have ) :

		error = None
		config = ConfigReader( file )
		
		does_not_have_sections = []
		for section in must_have:
			if not config.hasSection( section ):
				does_not_have_sections.append( section )
				
		if does_not_have_sections:
			error = 	"Error: Config file does not contain sections:- " + ", ".join( does_not_have_sections )
				
		return config, error
		
	def getConfigItem( self, name, config=None ):
		
		"""
			Check for value in the main section,
			then fall back to general section
		"""
		
		value = None
		
		if config == None:
			config = self.config
			
		if config.hasItem( self.config_main_section, name ) :
			value = config.item( self.config_main_section, name )
		elif config.hasItem( self.config_general_section, name ) :
			value = config.item( self.config_general_section, name )
		else:
			pass
			
		return value

	def debugging( self, config ) :
		
		debug = self.getConfigItem( "debug", config )
		if not debug:
			debug = False
		
		return debug
		
	def getCommandLine( self, must_have ) :

		command_line = CommandLine()
		error = None
		
		# check for process_id first as we use it to log - if we have problem report that first
		if not command_line.has( self.commandline_process_id ):
			error = 	"Error: Command line does not contain a " + self.commandline_process_id + "=<VALUE>. This is needed for logging." 
		else :
			value = command_line.get( self.commandline_process_id )
			parameter_error = self.checkParameter( self.commandline_process_id, 'number', value )
			
			if parameter_error:
				# See if we can recover (so we can report the error )
				result = re.search( r'^\d+', value )
				if result:
					process_id = result.group()
					command_line.set( self.commandline_process_id, process_id )
					
					parameter_error += " Attempted to *guess* correct process_id, found " + str( process_id ) + ". "
					
			error = parameter_error
					
		
		# Check other commandlines
		must_have_keys = must_have.keys()
		does_not_have_parameters = []
		for parameter in must_have_keys:
			if parameter != self.commandline_process_id:
				if not command_line.has( parameter ):
					does_not_have_parameters.append( parameter )
				
		if does_not_have_parameters:
			error = (error + " Also, " ) if error else "Error: "
			error += "Command line does not contain - " + "  ".join( [s + "=<VALUE>" for s in does_not_have_parameters] )
		
		else:
			for parameter in must_have_keys:
				if parameter != self.commandline_process_id :
					type = must_have[parameter]
					value = command_line.get( parameter )
					
					parameter_error = self.checkParameter( parameter, type, value )
						
					if parameter_error:
						error = (error + " " ) if error else "Error: "
						error += parameter_error + " "
		
		return command_line, error
	
	def checkParameter( self, parameter, type, value ) :
		parameter_error = None
		
		if not value:
			parameter_error = 'Error: Parameter "' + parameter + '" can not be empty.'
			
		else:
			if type == Step.type_folder :
				parameter_error = self.checkFolder( value )
			elif type == Step.type_file :
				parameter_error = self.checkFile( value )
			elif type == Step.type_number :
				parameter_error = self.checkNumber( value )
			elif type == Step.type_string or type == Step.type_ignore:
				parameter_error = None # anything goes.
			else :
				parameter_error = "Command line type not recognised. Should be set to folder, file, number, string or ignore."
				
			if parameter_error :
				parameter_error = 'Error: Parameter "' + parameter + '" - ' + parameter_error
	
		return parameter_error
	
	def checkNumber( self, number ):
		error = None
		
		try:
			float( number )
		except ValueError:
			error = 'Number "' + number + '" is not a number.'

		return error
	
	def checkFile( self, file ) :
		
		error = None
		
		if not os.path.exists( file ) :
			error = 'File "' + file + '" does not exist.'
			
		else:
			if not os.path.isfile( file ) :
				error = 'File "' + file + '" is not a file.'
			else:
				try:
					with open( file ) : pass
				except IOError:
					error = 'File "' + file + '" exists but unable to open it.'

		return error
		
	def checkFolder( self, folder ):
		
		error = None
		
		if not os.path.exists( folder ) :
			error = 'Folder "' + folder + '" does not exist.'
		else:
			if not os.path.isdir( folder ) :
				error = 'Folder "' + folder + '" is not a folder.'
				
		# PoToDo: Check theres something in it?

		return error
		
		
	def createLogging( s, just_file = False ):
		return s.getLoggingSystems( s.config, s.config_main_section, s.command_line, s.debug, s.name + "_logger", just_file )

	def recreateFileLogging( s ) :
		"""
			Used post detach (fork) to recreate file handler
		"""
		#logger = s.glogger.getLogger()
		#logger.removeHandler( s.glogger_handlers["rotating"] )
		
		#s.createLogging( True )
		
		
		
		
	def getLogger( self, config, id, debug ) :

		logger = logging.getLogger( id )
		
		if debug:
			logger.setLevel( logging.DEBUG )
		else:
			logger.setLevel( logging.INFO )
			
		return logger
			
			
		
	def addRotatingLog( self, config, config_main_section, command_line, logger, debug ):

		error = None
		
		try:
			log_max_bytes = int( self.getConfigItem( "log_max_bytes", config ) )
		except ValueError:
			log_max_bytes = 50000000
		
		try:	
			log_backup_count = int( self.getConfigItem( "log_backup_count", config ) )
		except ValueError:
			log_backup_count = 4
		
		log_file = config.item( config_main_section, "log" )
		
		try:
			rotating_logger_handler = logging.handlers.RotatingFileHandler( log_file, maxBytes=log_max_bytes, backupCount=log_backup_count )
			
			# Add Process ID to the log
			pid = "unknown"
			if command_line.has( self.commandline_process_id ) :
				pid = str( command_line.get(self.commandline_process_id) )
			
			rotating_logger_handler.setFormatter( logging.Formatter( "[ProcID " + pid + '] %(asctime)s (%(levelname)s)   %(message)s') )
			
			if debug :
				rotating_logger_handler.setLevel( logging.DEBUG )
			else:
				rotating_logger_handler.setLevel( logging.INFO )
				
			self.glogger_handlers["rotating"] = rotating_logger_handler
			logger.addHandler( rotating_logger_handler )
			
		except IOError:
			
			error = 'Error: Unable to open log file at : ' + log_file
		
		return error 
		
	def addEmailLog( self, config, config_main_section, logger ):
		
		log_email = self.getConfigItem( "log_email", config )
		
		if log_email :
			
			log_email_subject = self.getConfigItem( "log_email_subject", config )
			if not log_email_subject:
				log_email_subject = "Goobi Error " + self.name
				
			email_logger_handler = logging.handlers.SMTPHandler( "smtp.ox.ac.uk", logger.name + "@goobi.bodleian.ox.ac.uk", log_email, log_email_subject)
			email_logger_handler.setLevel( logging.WARNING )
			
			self.glogger_handlers["email"] = email_logger_handler
			logger.addHandler( email_logger_handler )
		
		
	def getGoobiLogger( self, config, command_line, logger, debug ):
		
		if command_line.has( self.commandline_process_id ):
			glogger = GoobiLogger( config.goobi.host, config.goobi.passcode, command_line.get(self.commandline_process_id), logger )

			if debug :
				glogger.debugging()
		else:
			glogger = logger
			
		return glogger
		
	def getLoggingSystems( self, config, config_main_section, command_line, debug, id, just_file=False ):
		"""
			Creating file, email and goobi logging.
			
			just_file is so we can recreate the file logger after we detach the prcess, when we detach we need to close all the open files. The other loggers are unaffected.
		"""
		#
		# Create our base logger
		#
		logger = self.getLogger( config, id, debug )
		
		
		if not just_file :
		
			#
			# Email Logger
			#
			self.addEmailLog( config, config_main_section, logger )		
		
		#
		# Create rotating file log
		#
		error = self.addRotatingLog( config, config_main_section, command_line, logger, debug )
		if error:
			return logger, error # Logger will log the error to the email log as the file handler has failed

		if not just_file:
		
			#
			# Get Goobi Logger (if able)
			#
			logger = self.getGoobiLogger( config, command_line, logger, debug )
		
		return logger, None
	
	
	def error_message( self, message ):
		self.error( message )
	def error( self, message ):
		if self.glogger:
			self.glogger.error( message )
		self.debuggingPrint( "Error: " + str(message) )
		
	def warning_message( self, message ):
		self.warning( message )
	def warning( self, message ):
		if self.glogger:
			self.glogger.warning( message )
		self.debuggingPrint( "Warning: " + str(message) )
		
	def info_message( self, message ):
		self.info( message )
	def info( self, message ):
		if self.glogger:
			self.glogger.info( message )
		self.debuggingPrint("Info: " + str(message) )
		
	def debug_message( self, message ):
		if self.glogger:
			self.glogger.debug( message )
		self.debuggingPrint("Debug: " + str(message) )
		
	def debuggingPrint( self, message ):
		if self.debug:
			print message
		
