#!/usr/bin/env python



import subprocess
import time
from subprocess import Popen
import sys
import os

TIMEOUT = 30 # timeonut handles the main loop 60s fails on NFS data reads 
ZO_SCIPION_HOME="/dls_sw/apps/scipion/1_2_1_headless/scipion/zocalo"


def run_zocalo_gautomatch():
    script = ZO_SCIPION_HOME + "/" + "zoc_gautomatch_submit.py"
    args = sys.argv[1:]
    #looking for the output of the processs
    automatch_file = str(args[0]).replace('.mrc','_automatch.star')




    # TODO: add the part of exit where script exits after creating png of whatever 

    cmd = ('source /etc/profile.d/modules.sh;'
           'module load python/ana;'
           'python ' + script + " "
           )

    print(cmd + " ".join(args))

    # submit recipie --this will always be true so don't check for exit status 

    p1 = Popen(cmd + " ".join(args), shell=True)
    p1.wait()


   
    out = p1.communicate()[0]
    print(out)

    import time
    
    found = False
    start_time = time.time()
    while not found:
    	if os.path.exists(automatch_file):
    		found = True
    		break
    	else:
		print("File not found, waiting...")
    		time.sleep(10)
# whether sucess or failure exit with 0 otherwise the main scipion thread does not move on the next micrograph
    	if (time.time() - start_time) > TIMEOUT:
                print('timeout exceeded skipping image')
    		sys.exit(0)

    return out

   


if __name__ == '__main__':

    extra_wd = run_zocalo_gautomatch()
