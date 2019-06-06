

# zocalo.service
#   Process a datacollection
#

from __future__ import absolute_import, division, print_function

import json
import sys
import os
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


  stomp = StompTransport()

  message = { 'recipes': [],
              'parameters': {},
            }
  # Build a custom recipe 

  #remove trailing whitespaces causes isssues in -Gpu
  #params_without_spaces = list(str(i).rstrip() for i in sys.argv[1:])


  recipe = {}
  recipe['1'] = {}
  recipe['1']['service'] = "Scipion_MotionCor2"
  recipe['1']['queue'] = "scipilo.ScipionMotionCor2"
  recipe['1']['parameters'] = {}
  recipe['1']['parameters']['arguments'] = sys.argv[1:] #params_without_spaces
  recipe['1']['parameters']['cwd'] = os.getcwd()
  recipe['start'] = [[1, []]]




  message['custom_recipe'] = recipe



  send_current_dir_to_bash()


  stomp.connect()

  
  #make a valid zocalo recipe by passing the dict 
  test_valid_recipe = workflows.recipe.Recipe(recipe)
  test_valid_recipe.validate()



  stomp.send(
    'processing_recipe',
    message
  )



