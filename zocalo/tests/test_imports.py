#!/usr/bin/env python

from __future__ import print_function

try:
    import scipilo
    import scipilo.consumers

except ImportError as error :
    print(error.__class__.__name__ + ": " + error.message)


try:
    from scipilo.consumers.ispyb_scipion_consumer_project_stop import ScipionRunner
    from scipilo.consumers.zoc_gautomatch_consumer import GautomatchRunner
    from scipilo.consumers.zoc_gctf_consumer import GctfRunner
    from scipilo.consumers.zoc_relion_refine_consumer import Relion2DRunner
    print("all imports successful")

except ImportError as error:
    print(error.__class__.__name__ + ": " + error. message)




