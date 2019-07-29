#!/bin/bash
. /etc/profile.d/modules.sh
module load dials
cd /dls_sw/apps/scipion/1_2_1_headless/scipion/zocalo/scipilo/consumers
dials.python bl_start_services.py -s ScipionRunner --live
