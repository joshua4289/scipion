from __future__ import absolute_import, division, print_function
from workflows.services.common_service import CommonService
import workflows.recipe


class ScipionRunnerClearQueue(CommonService):
    '''A zocalo service for running Scipion'''

    # Human readable service name
    _service_name = "Queue Clear Runner"

    # Logger name
    _logger_name = 'scipion.zocalo.services.runner'

    def initializing(self):
        '''Subscribe to the per_image_analysis queue. Received messages must be acknowledged.'''
        queue_name = "scipilo.ScipionDev"
        self.log.info("queue that is being listended to is %s" % queue_name)
    
        workflows.recipe.wrap_subscribe(self._transport,queue_name,self.consume_message, acknowledgement=True, log_extender=self.extend_log,allow_non_recipe_messages=True)


    def consume_message(self,rw,header,message):
        self.log.info('Clearing the queue')
        #self.log.info(message)
        self.transport.ack(header)
        self._shutdown
        self.log.info('shutdown consumer')








