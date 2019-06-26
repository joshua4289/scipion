from __future__ import absolute_import, division, print_function
from workflows.services.common_service import CommonService
import workflows.recipe
from subprocess import PIPE, Popen

try:
    from pathlib2 import Path
except:
    from  pathlib import Path


# Active MQ Scipion Consumer started as gda2

class ScipionRunnerdev(CommonService):
    '''A zocalo service for running Scipion'''

    # Human readable service name
    _service_name = "Scipion_json_finder"

    # Logger name
    _logger_name = 'scipion.zocalo.services.runner'

    def initializing(self):
        """Subscribe to the per_image_analysis queue. Received messages must be acknowledged.

		"""

        # Add a .project file in the session which is an updated list/ json of running_projects . Only 1 project will run  all the other processed projects will be killed
        self.running_projects = list()

        queue_name = "scipilo.ScipionDev"

        self.log.info("queue that is being listended to is %s" % queue_name)


        workflows.recipe.wrap_subscribe(self._transport, queue_name,
                                        self.find_json_from_recipe, acknowledgement=True, log_extender=self.extend_log,
                                        allow_non_recipe_messages=True)








    def find_json_from_recipe(self, rw, header, message):
        self.log.info("Start running scipion json finder ")

        import subprocess
        from subprocess import Popen

        # get the parameters
        # rw is None
        # header is the timestamp

        #json_file path is read from the message

        json_file = message['scipion_workflow']
        json_path = (Path(json_file))

        self.log.info("Initial start processing json %s " %json_file)
        self.log.info("Finish running scipion workflow finder ")


        #this is the main callback
        self.create_project_and_process(json_path)





        #acknowledge the header directly this is not a 'recipe'
        #so cannot use any of the recipe acknowledge mechanisms

        self.transport.ack(header)

        return json_path

    # some use in the near future
    def find_session_id(self,json_path):
        import re
        reg1 = re.compile(r'^[a-zA-Z]*[0-9].*')
        matches = list (filter(reg1.match,json_path.parts))

        session_id = matches[-1]

        return session_id


    @staticmethod
    def create_timestamp():
        # type: () -> str
        import datetime
        return datetime.datetime.now().strftime("%y%m%d%H%M%S")


    @staticmethod
    def sleeper(seconds):
        import time
        return time.sleep(seconds)




    def _find_gain_path(self):

        ''' looks for gain file in a pre-defined location should be relative to where the the other parts '''

        pass


    def _on_message(self,project_name,visit_dir):

        ''' On new start project message stop  previous running projects '''

        self.log.info("Scipion running projects are ".format(self.running_projects))

        #TODO: On a new message write out the in-memory list to .projects/projects.txt


        projects_file = visit_dir/'.projects'/'project.txt'

        #stop_project_list = []
        with open (str(projects_file) , 'a+') as pf:

            pf.write(project_name)
            pf.write("\n")
            self.log.info("project added to .projects file is %s " % project_name)




        with open(str(projects_file),'r') as pf:
            live_project_list = pf.read().split()

            self.log.info("list of projects is %s " % live_project_list)



            #pop the first item and work your way down last item is latest project
            while len(live_project_list) > 1:
                to_stop = live_project_list.pop(0)

                self.log.info("%s will be stopped " % to_stop)
                stop_project_args = ['cd', '$SCIPION_HOME;', 'scipion', '--config $SCIPION_HOME/config/scipion.conf','python', 'scripts/stop_project.py', to_stop]
                stop_project_cmd = self._create_prefix_command(stop_project_args)



                try:
                    p1 = Popen(stop_project_cmd,shell=True)
                    out,err = p1.communicate()



                    if p1.returncode != 0:
                        self.log.info("%s could not be stopped " %to_stop)
                        self.log.info("%s was returned by stop project " %out )
                        self.log.info("%s error was returned by stop_project " %err)
                except:
                    pass

                if len(live_project_list) == 1:
                    self.log.info("project run is %s" %live_project_list)








    def _start_refresh_project(self,project_name):
        """ starts the script in scripts/refresh_project.py """
        refresh_project_args = ['cd', '$SCIPION_HOME;', 'scipion','--config $SCIPION_HOME/config/scipion.conf', 'python','scripts/refresh_project.py', project_name]

        refresh_project_cmd = self._create_prefix_command(refresh_project_args)


        return refresh_project_cmd



    def _create_prefix_command(self, args):

        """Prefixes command to run loading modules to setup env """

        cmd = ('source /etc/profile.d/modules.sh;'
               'module unload python/ana;'
               'module unload scipion/release-1.2.1-headless;'
               'module load scipion/release-1.2.1-headless;'
               'export SCIPION_NOGUI=true;'
               'export SCIPIONBOX_ISPYB_ON=True;'
               )
        return cmd + ' '.join(args)




    #  UTIL FUNCTIONS
    #get methods grab values from json
    # calculate methods are inferred
        #
    def get_pixel_size(self, ispyb_json):
        for it in ispyb_json:
            # print("***************%r" %type(it))
            if it['object.className'] == "ProtImportMovies":
                samplingRate = it['samplingRate']
                return samplingRate

    def get_particle_size(self, ispyb_json):
        for it in ispyb_json:

            if it['object.className'] == "ProtGautomatch":
                particleSize = it['particleSize']
                return particleSize

    def calculateBoxSize(self, samplingRate, particleSize):
        emanBoxSizes = [32, 36, 40, 48, 52, 56, 64, 66, 70, 72, 80, 84, 88,
                        100, 104, 108, 112, 120, 128, 130, 132, 140, 144, 150, 160, 162, 168, 176, 180, 182, 192,
                        200, 208, 216, 220, 224, 240, 256, 264, 288, 300, 308, 320, 324, 336, 338, 352, 364, 384,
                        400, 420, 432, 448, 450, 462, 480, 486, 500, 504, 512, 520, 528, 546, 560, 576, 588,
                        600, 640, 648, 650, 660, 672, 686, 700, 702, 704, 720, 726, 728, 750, 768, 770, 784,
                        800, 810, 840, 882, 896, 910, 924, 936, 972, 980, 1008, 1014, 1020, 1024]

        # convert largest axis/diameter to pixel then add tolerance  factor. You are returning some boxsize in the list .
        # it's not a performance consideration because it will be scaled down


        exactBoxSize = int((particleSize * 2) / samplingRate) * 1.2
        for bs in emanBoxSizes:
            if bs >= exactBoxSize:
                # self.log.info("############# %r " %type(samplingRate))
                # self.log.info("########### %r " %type(particleSize))
                # self.log.info("-------------------Box size returned from within the function is %r" %type(bs))
                return int(bs)

    def calculate_ctfest_range(self, samplingRate):

        if samplingRate < 1:
            return (0.01, 0.35)
        else:
            return (0.03, 0.35)

    def load_json(self, json_path):
        # Path --> json_dict
        import json
        json_data = json.load(open(str(json_path)))
        return json_data

        # should be __main__() function

    def create_project_and_process(self,json_path):

        ''' start processing by calling various functions  '''

        timestamp = self.create_timestamp()

        # go 2 levels up from .ispyb/processing to visit dir

        visit_dir = json_path.parents[2]

        project_name = visit_dir.stem + '_' + timestamp
        workspace_dir = visit_dir / 'processed'
        self.log.info("visit dir is %s" % visit_dir)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        workflow = (workspace_dir / ("scipion_template_" + timestamp)).with_suffix(".json")

        special_project_dir = visit_dir/'.projects'
        special_project_dir.mkdir(parents=True, exist_ok=True)

        # This is important because of ACL's on the BEAMLINE has to get correct groups
        # instead of running with the json directly we need to modify some parms from what is posted to determine box size
        # instead of the copy load json into memory and make modifications

        #LOADED IsPyB JSON

        json_to_modify = self.load_json(json_path)

        # NOTE : These should only be modifications pertaining to CTF fixes < 0.5 A/Px

        #TODO: load into memory
        #TODO: caluclate boxSize and CTF ranges
        #TODO: write out the initial file correctly


        boxSize = self.calculateBoxSize(self.get_pixel_size(json_to_modify),self.get_particle_size(json_to_modify))
        lowRes, highRes = self.calculate_ctfest_range(self.get_particle_size(json_to_modify))


        for it in json_to_modify:

            self.log.info("%r json keys  of type " %it.keys())
            self.log.info("%s is of type " %type(it['object.className']))


            if it['object.className'] == "ProtCTFFind":
                it['lowRes'] = lowRes
                it['highRes'] = highRes
                self.log.info(" TEST CTF range is  is %r" % self.calculateBoxSize(self.get_pixel_size(json_to_modify),
                                                                             self.get_particle_size(json_to_modify)))
            if it['object.className'] == "ProtGautomatch":
                it['boxSize'] = boxSize
                self.log.info(" TEST BOX size is %r" % self.calculateBoxSize(self.get_pixel_size(json_to_modify),self.get_particle_size(json_to_modify)))

            if it['object.className'] == "ProtRelionExtractParticles":
                it['boxSize'] = boxSize
                self.log.info("BoxSize is %s" %(boxSize))
                self.log.info(" TEST pixel size is %r" %self.get_pixel_size(json_to_modify))
                self.log.info(" TEST particle size is %r" %self.get_particle_size(json_to_modify))




        test_box = self.calculateBoxSize(1.0,200)
        self.log.info("%s,%s is special val" %(lowRes,highRes))
        self.log.info('boxsize test value is %r '%test_box)
        test_box = self.calculateBoxSize(2.0, 200)
        self.log.info('boxsize test value is %r ' % test_box)

        # substitutions in  config file (inplace)
        #
        #
        import shutil,json

        self.log.info("%s is workflow" %workflow)

        workflow_tmp = str(workflow)+'.tmp'

        #write out a .tmp file and copy it
        with open(workflow_tmp,'w') as outfile:
            json.dump(json_to_modify,outfile,indent=4)


        if Path(workflow_tmp).exists:
            shutil.copy(str(workflow_tmp), str(workflow))
            self.log.info('*****************TMP WF is %r' %workflow_tmp)
            self.log.info('overwrite with changes of %s was completed' %(workflow))

        create_project_args = ['cd', '$SCIPION_HOME;','scipion', '--config $SCIPION_HOME/config/scipion.conf','python','scripts/create_project.py',
                               project_name, str(workflow), str(workspace_dir)]


        create_project_cmd = self._create_prefix_command(create_project_args)

        p1 = Popen(create_project_cmd, cwd=str(workspace_dir), stderr=PIPE, stdout=PIPE, shell=True)
        self.sleeper(2)
        global out_project_cmd ,err_project_cmd
        out_project_cmd, err_project_cmd = p1.communicate()

        self.log.error(err_project_cmd)
        self.log.info("Create project script SUCCESS")
        self.log.info("created project with command %s" %create_project_cmd)
        self.log.info('processing started using parmaters in %s ' %workflow)
        self.log.info('scipion  project started %s'%workspace_dir)






        if p1.returncode != 0:

            self.log.error("Could not create project at {}".format(workspace_dir))
            self.log.error("create project error at {}".format(out_project_cmd,err_project_cmd))
            self.log.error('main thread consumer being killed')



        #TODO: kill _the consumer with an exit the controller logic will restart it


        else:
        #kill other processing projects in the visit
            self._on_message(str(project_name), visit_dir)



        schedule_project_args = ['cd', '$SCIPION_HOME;', 'scipion','--config $SCIPION_HOME/config/scipion.conf', 'python',
                                 '$SCIPION_HOME/scripts/schedule_project.py', project_name]
        schedule_project_cmd = self._create_prefix_command(schedule_project_args)
        # comment out if need be for testing

        #Popen(schedule_project_cmd, cwd=str(workspace_dir), shell=True)

        self.log.info("does not launch schedule project TESTING ")
        self.sleeper(2)
        self.log.info("schedule command is ".format(schedule_project_cmd))

        refresh_project_cmd = self._start_refresh_project(project_name)
        Popen(refresh_project_cmd, cwd=str(workspace_dir), shell=True)




