from __future__ import absolute_import, division, print_function
from workflows.services.common_service import CommonService
import workflows.recipe
from subprocess import PIPE, Popen
import json
import os, re

# Active MQ Scipion Consumer started as gda2

class GctfRunner(CommonService):
    '''A zocalo service for running Scipion'''

    # Human readable service name
    _service_name = "Gctf_runner"

    # Logger name
    _logger_name = 'Gctf.zocalo.services.runner'

    def initializing(self):
        """Subscribe to the per_image_analysis queue. Received messages must be acknowledged.

		"""
        queue_name = "Gctf_runner"
        self.log.info("queue that is being listended to is %s" % queue_name)
        workflows.recipe.wrap_subscribe(self._transport, queue_name,
                                        self.run_Gctf, acknowledgement=True, log_extender=self.extend_log,
                                        allow_non_recipe_messages=True)

    def run_Gctf(self, rw, header, message):

        self.log.info("Start running Gctf Zocalo")

        from subprocess import Popen

        # get the parameters
        session = rw.recipe_step['parameters']

        self.log.info(session)
        arguments = session['arguments']
        scipion_dir = session['cwd']

        self.log.info("Scipion Dir is %s" % scipion_dir)
        self.log.info("Arguments are '%s'" % ' '.join(arguments))

        # Compose the command and the environment
        # Non-phase plate consumer for Gctf 
        cmd = ('source /etc/profile.d/modules.sh;'
               'module load EM/Gctf/1.06;'
               'Gctf '
               ) 
        cmd += ' '.join(arguments)

        self.log.info(cmd)

        # Run the command
        from subprocess import PIPE
        p1 = Popen(cmd ,cwd=scipion_dir,shell=True)

        out_project_cmd, err_project_cmd = p1.communicate()
        self.log.info("Gctf errors are :%s" %(err_project_cmd))
			        

        # Read output and feedback ...but GCTF does not do this
        # while p1.poll() is None: #True or p1.returncode != 0
        #     print(p1.stdout.readline())
        #
        # t_queue = (rw.recipe[rw.recipe_pointer + 1]['queue'])

        p1.wait()
        print ("SCIPION WORK DIR IS  %s" %(scipion_dir))
        

        done_file_name = os.path.join(scipion_dir, 'done.tmp')
        with open(done_file_name, 'w') as done_file:
            done_file.write("Complete\n")

        self.log.info("Wrote log file to '%s'" % (done_file_name))

        self.log.info("Finish running Gctf Zocalo")
        
        rw.transport.ack(header)
        

        
    def shutdown_consumer(self):
        ''' Shutdown Consumer based on the timeout mentioned in the Import step of workflow '''

        pass

