# -*- coding: utf-8 -*-

# Example calling from Goobi:
# /usr/bin/python /opt/digiverso/goobi/scripts/databank/test_goobi_logging.py processid={processid} message=test

import config_ini

from cli.command_line import CommandLine
#from goobi.goobi_communicate import GoobiCommunicate
from goobi.goobi_logger import GoobiLogger
from config.config_reader import ConfigReader

goobi_commandline = CommandLine()
config = ConfigReader( config_ini.file )
#com = GoobiCommunicate( config.goobi.host, config.goobi.passcode, goobi_commandline.processid )
logger = GoobiLogger( config.goobi.host, config.goobi.passcode, goobi_commandline.process_id )

logger.error( "An example *error* message" )
logger.info( "An example  *info* message" )
logger.user( "An example *user* message" )
logger.debug(  "An example *debug* message" )

logger.warning( "An example *warning* message. Actually *info* in Goobi."  )

logger.debug( "Message on command line: " + goobi_commandline.message )


print "Messages sent."