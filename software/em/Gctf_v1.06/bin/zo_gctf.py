#!/usr/bin/env python


# call dials python and submit
import subprocess
import time
from subprocess import Popen
import sys
import os

ZO_SCIPION_HOME = "/dls_sw/apps/scipion/1_2_1_headless/scipion/zocalo"


def run_zocalo_gctf():
    script = ZO_SCIPION_HOME + "/" + "zoc_gctf_submit.py"
    args = sys.argv[1:]

    # TODO: add the part of exit where script exits after creating png of whatever

    cmd = ('source /etc/profile.d/modules.sh;'
           'module load python/ana;'
           'python ' + script + " "
           )

    print(cmd + " ".join(args))

    # submit recipie --this will always be true so don't check for exit status

    p1 = Popen(cmd + " ".join(args), shell=True, stdout=subprocess.PIPE)
    p1.wait()
    import time
    time.sleep(1)
    # submission to zocalo queue

    out = p1.communicate()[0]
    return out


if __name__ == '__main__':
    import os

    extra_done_file = 'done_gctf.tmp'
    extra_wd = run_zocalo_gctf()

    while not os.path.exists(extra_done_file):
        time.sleep(5)

    if os.path.exists(extra_done_file):
        os.remove(extra_done_file)
        sys.exit(0)
