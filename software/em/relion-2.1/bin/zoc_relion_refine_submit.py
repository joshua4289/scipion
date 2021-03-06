#!/usr/bin/env python

# zocalo.service
#   Process a datacollection
# RELION2D RECIPIE SUBMITTER

from __future__ import absolute_import, division, print_function

import json
import sys
import os
import uuid
from optparse import SUPPRESS_HELP, OptionParser

import workflows
import workflows.recipe
from workflows.transport.stomp_transport import StompTransport


def lazy_pprint(*args, **kwargs):
  from pprint import pprint
  pprint(*args, **kwargs)

def send_current_dir_to_bash():
  print (os.getcwd()) #print is important to set the bash variable
  return os.getcwd()

if __name__ == '__main__':

  default_configuration = '/dls_sw/apps/zocalo/secrets/credentials-live.cfg'
  # override default stomp host
  try:
    StompTransport.load_configuration_file(default_configuration)
  except workflows.Error as e:
    print("Error: %s\n" % str(e))

  #StompTransport.add_command_line_options(parser)
  #(options, args) = parser.parse_args(sys.argv[1:])
  
 
  stomp = StompTransport()

  message = { 'recipes': [],
              'parameters': {},
            }
  # Build a custom recipe 
  recipe = {}
  recipe['1'] = {}
  recipe['1']['service'] = "Scipion_Relion2D"
  recipe['1']['queue'] = "scipilo.ScipionRelion2D"
  recipe['1']['parameters'] = {}
  recipe['1']['parameters']['arguments'] = sys.argv[1:]
  recipe['1']['parameters']['cwd'] = os.getcwd()
  
  # reply_to = 'transient.relion.%s'%str(uuid.uuid4())
  # recipe['1']['output'] = 2
  # recipe['2'] = {}
  # recipe['2']['service'] = "relion_refine_call_back"
  # recipe['2']['queue'] = reply_to
  # recipe['2']['parameters'] = {}
  # recipe['2']['output'] = 3
  # recipe['3'] = {}

  recipe['start'] = [[1, []]]
 



  message['custom_recipe'] = recipe



  

  stomp.connect()

  test_valid_recipe = workflows.recipe.Recipe(recipe)
  test_valid_recipe.validate()



  stomp.send(
    'processing_recipe',
    message
  )


  
  

