#!/usr/bin/env python
# zocalo.service
#   Process a datacollection
#

from __future__ import absolute_import, division, print_function

import json
import sys
import os
import re
from optparse import SUPPRESS_HELP, OptionParser

import workflows
import workflows.recipe
from workflows.transport.stomp_transport import StompTransport
import uuid


# /dls/tmp/gda2/dls/m02/data/2018/em12345-01/processed/em12345-01_20181107_1600/Runs/000122_ProtGctf/tmp/GridSquare_401K_Data_FoilHole_5419591_Data_5417705_5417706_20180306_2106-140228_aligned_mic.mrc/ctfEstimation.txt
# Runs/000122_ProtGctf/extra/GridSquare_401K_Data_FoilHole_5419591_Data_5417705_5417706_20180306_2106-140228_aligned_mic/ctfEstimation.txt

def get_output_file(input_file):
   

    tmp1 = str(os.path.join(os.getcwd(),
                            os.path.dirname(input_file),
                            os.path.splitext(os.path.basename(input_file))[0],
                            'ctfEstimation.txt'))

    corr_tmp1 = re.sub('(\d+.)ProtGctf/tmp', r'\1ProtGctf/extra', tmp1)

    
    output_file = os.path.join(os.getcwd(),
                               os.path.dirname(input_file),
                               os.path.splitext(os.path.basename(input_file))[0],
                               'ctfEstimation.txt')
    # print(output_file)

    return corr_tmp1


def lazy_pprint(*args, **kwargs):
    from pprint import pprint
    # pprint(*args, **kwargs)




if __name__ == '__main__':

    default_configuration = '/dls_sw/apps/zocalo/secrets/credentials-live.cfg'
    # override default stomp host
    try:
        StompTransport.load_configuration_file(default_configuration)
    except workflows.Error as e:
        print("Error: %s\n" % str(e))

    # StompTransport.add_command_line_options(parser)
    # (options, args) = parser.parse_args(sys.argv[1:])
    stomp = StompTransport()

    output_file = get_output_file(sys.argv[-1])

    message = {'recipes': [],
               'parameters': {},
               }
    # Build a custom recipe
    recipe = {}
    recipe['1'] = {}
    recipe['1']['service'] = "Scipion_Gctf"
    recipe['1']['queue'] = "scipilo.ScipionGctf"
    recipe['1']['parameters'] = {}
    recipe['1']['parameters']['arguments'] = sys.argv[1:] + ['>', output_file]
    recipe['1']['parameters']['cwd'] = os.getcwd()

    message['custom_recipe'] = recipe

    
    recipe['start'] = [[1, []]]

    stomp.connect()

    test_valid_recipe = workflows.recipe.Recipe(recipe)
    test_valid_recipe.validate()

    stomp.send(
        'processing_recipe',
        message
    )

    
    print(output_file)

