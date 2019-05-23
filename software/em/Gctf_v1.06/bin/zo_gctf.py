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
    time.sleep(5)
    # submission to zocalo queue

    out = p1.communicate()[0]


    return out

    # TODO:1: get the scipion directory from the recipie from the ['cwd'] instead of the command
    # 2. If it is the top directory workout the paths to find the extra folder and look for the done.txt inside the folder for a fiven image


if __name__ == '__main__':
    import os

    user = os.environ.get('USER')
    tmp_log_file = os.path.join('/dls/tmp/', user, 'zo_gctf_log.tmp')

    with open(tmp_log_file, 'w') as tmplog:

        tmplog.write("WE ARE STARTING ZO_GCTF\n")
        tmplog.write("CWD is %s\n" % (os.getcwd()))
        tmplog.flush()

        # created in scipion project folder

        extra_done_file = 'done.tmp'
        tmplog.write("THIS IS '%s' \n" % (extra_done_file))

        extra_wd = run_zocalo_gctf()

        tmplog.write("extra_done file is " + extra_done_file + "\n")
        while not os.path.exists(extra_done_file):
            tmplog.write("waiting for '%s'\n" % os.path.realpath(extra_done_file))
            tmplog.flush()
            time.sleep(5)

        tmplog.write("EXITING!!\n")
        # remove the extra done file when program1


    if os.path.exists(extra_done_file):
        os.remove(extra_done_file)
        sys.exit(0)




