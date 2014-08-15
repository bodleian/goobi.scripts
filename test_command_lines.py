# -*- coding: utf-8 -*-

import sys
from cli.command_line import CommandLine

goobi_cm = CommandLine( sys.argv )

message = ''
for para in goobi_cm._parameters: 
	message += para + " = " + goobi_cm._parameters[para] + "\n"
	
print message