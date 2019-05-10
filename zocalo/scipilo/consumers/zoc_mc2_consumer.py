from __future__ import absolute_import, division, print_function
from workflows.services.common_service import CommonService
import workflows.recipe
from subprocess import PIPE, Popen
import json
import os, re

# Active MQ Scipion Consumer started as gda2

class ScipionMotionCor2(CommonService):
    '''A zocalo service for running Scipion'''

    # Human readable service name
    _service_name = "Scipion_MotionCor2"

    # Logger name
    _logger_name = 'scipion.motioncor2.zocalo.services.runner'

    def initializing(self):
        """Subscribe to the per_image_analysis queue. Received messages must be acknowledged.

		"""
        queue_name = "ScipionMotionCor2"
        self.log.info("queue that is being listended to is %s" % queue_name)
        workflows.recipe.wrap_subscribe(self._transport, queue_name,
                                        self.run_MotionCor2, acknowledgement=True, log_extender=self.extend_log,
                                        allow_non_recipe_messages=True)

    def run_MotionCor2(self, rw, header, message):

        self.log.info("Start running MotionCor2 Zocalo")

        import subprocess
        from subprocess import Popen

        # get the parameters

        session = rw.recipe_step['parameters']

        arguments = session['arguments']
        scipion_dir = session['cwd']

        self.log.info("Scipion Dir is %s" % scipion_dir)

        # modify the GPU flag to be the correct GPU for this consumer

        #find the next index after -Gpu
        #SGE_HGR_GPU gives GPU0 GPU1 if 2 gpu system 

       
        gpu_index = arguments.index('-Gpu') + 1
        
        #gives 0
        #this works with qloin and ssh because if sge_hgr variable not set it will default to gpu1 and the value u get will be 1
        #but in qsub where sge_hgr is set value you get is 0
        #convoluted logic dependent on not set rather than set 
        #TODO:convert string to list and find number of GPU's use range to then set GPU'ids

        arguments[gpu_index] = os.getenv('SGE_HGR_gpu', 'GPU1')[8]

        self.log.info("Arguments are '%s'" % ' '.join(arguments))

        cmd = ('source /etc/profile.d/modules.sh;'
               'module load EM/MotionCor2/1.1.0;'
               'MotionCor2 '
               ) 

        cmd += ' '.join(arguments)

        self.log.info(cmd)
   
        p1 = Popen(cmd + ' '.join(arguments), cwd=scipion_dir,shell=True)
        out_project_cmd, err_project_cmd = p1.communicate()

        p1.wait()


        self.log.info("Finish running MotionCor2 Zocalo")
        rw.transport.ack(header)
        rw.send([])

    
    def shutdown_consumer(self):
        ''' Shutdown Consumer based on the timeout mentioned in the Import step of workflow '''

        pass

