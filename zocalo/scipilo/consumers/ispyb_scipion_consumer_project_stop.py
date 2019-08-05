from __future__ import absolute_import, division, print_function
from workflows.services.common_service import CommonService
import workflows.recipe
from subprocess import PIPE, Popen
import os

try:
    from pathlib2 import Path
except:
    from  pathlib import Path


# Active MQ Scipion Consumer started as gda2

class ScipionRunner(CommonService):
    '''A zocalo service for running Scipion'''

    # Human readable service name
    _service_name = "Scipion_json_finder"

    # Logger name
    _logger_name = 'scipion.zocalo.services.runner'

    def initializing(self):
        """ some special initalizing function  """


        #each instance of the runner has to be initialized
        self.running_projects = list()

        queue_name = "scipilo.ScipionDev"

        self.log.info("queue that is being listened to is %s" % queue_name)

        #self._transport.subscribe(queue_name,self.find_json_from_recipe)
        workflows.recipe.wrap_subscribe(self._transport, queue_name,
                                        self.find_json_from_recipe, acknowledgement=True, log_extender=self.extend_log,
                                        allow_non_recipe_messages=True)








    def find_json_from_recipe(self, rw, header, message):

        """ Reads the workdlow file from ispyb and launches the main function """

        self.log.info("Start running scipion json finder ")

        import subprocess
        from subprocess import Popen

        # get the parameters
        # rw is None
        # header is the timestamp

        json_file = message['scipion_workflow']
        json_path = (Path(json_file))

        self.log.info("Initial start processing json %s " %json_file)
        self.log.info("Finish running scipion workflow finder ")




        project_name = self.create_project_and_process(json_path)







        self.transport.ack(header)

        return json_path


    def find_session_id(self,json_path):
        import re
        reg1 = re.compile(r'^[a-zA-Z]*[0-9].*')
        matches = list (filter(reg1.match,json_path.parts))
        # this is general to allow changes in format for future sessions
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




    def _find_gain_path(self,folder):

        '''looks in processing/ for gain file in a pre-defined location should be relative to where the the other parts '''

        import os
        for root, dir, files in os.walk(folder):

            for f in files:

                if "gain" or "Gain" in str(f):

                    if f.endswith(('mrc', 'tif', 'tiff', 'dm4')):
                        self.log.info("the gain path found was at %s" %(os.path.join(root,f)))
                        return os.path.join(root, f)






    def _convert_gain(self,ip_gain_file,op_gain_file):
        """  convert a dm4 or tiff gain to mrc helper function """

        cmd = ('source /etc/profile.d/modules.sh;'
               'module unload EM/imod;'
               'module load EM/imod;')

        #gain_file = os.path.join(op_gain_file,'Gain.mrc')


        global imod_convert_fmt



        if str(ip_gain_file.endswith('.dm4')):
            imod_convert_fmt = ['dm2mrc', ip_gain_file, str(op_gain_file)]

        if str(ip_gain_file.endswith(('.tiff','.tif'))):
            imod_convert_fmt = ['tif2mrc', ip_gain_file, str(op_gain_file)]


        convert_command = cmd + ' '.join(imod_convert_fmt)
        self.log.error(convert_command)


        p1 = Popen(convert_command, shell=True)
        out,err = p1.communicate()
        try:
            p1.wait(timeout=90)
        except subprocess.SubprocessError as e:
            self.log.error(e)

        if p1.returncode == 0:
            self.log.info("CONVERT GAIN :command run was %s " %convert_command)
            self.log.info("%s was  properly converted " % ip_gain_file)

            return op_gain_file

        else:
            self.log.info("Error in conversion %s" % err)
            self.log.info("error in gain conversion  exit ")




    def on_message(self,project_name,visit_dir):
        ''' On new start project message stop  previous running projects '''

        self.log.info("Scipion running projects are ".format(self.running_projects))

        #On a new message write out the in-memory list to .projects/projects.txt



        projects_file = visit_dir/'.projects'/'project.txt'

        #stop_project_list = []
        with open (str(projects_file) , 'a+') as pf:

            pf.write(project_name)
            pf.write("\n")
            self.log.info("project added to .projects file is %s " % project_name)



        #Read txt file and stop project

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
            except err as e:
                self.log.info("projects stopping error ")
                self.log.info(e)

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
               'module unload scipion/scipion/2.0-zo;'
               'module load scipion/2.0-zo;'   
               'export SCIPION_NOGUI=true;'
               'export SCIPIONBOX_ISPYB_ON=True;'
               )
        return cmd + ' '.join(args)

    def load_json(self, json_path):
       # Path --> json_dict
       import json
       json_data = json.load(open(str(json_path)))
       return json_data







    #this should be the main method

    def create_project_and_process(self,json_path):

        ''' start processing by calling various functions  '''

        import shutil
        import os


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


        #TODO: copy once file has finished writing to disk SuperRes takes a sec

        user_dir =  visit_dir / 'processing'


        #gda2 can't write in user space so write in processed



        ip_gain_file = self._find_gain_path(str(user_dir))
        op_gain_file = Path(workspace_dir / 'Gain.mrc')


        if ip_gain_file is not None:
            # call convert only if gain is found else continue with kick-off if no gain file it should be a Falcon session

            mrc_converted_gain = self._convert_gain(ip_gain_file,op_gain_file)
            self.log.info("gain file read in from processing and writen to %s" %mrc_converted_gain)




        json_to_modify = self.load_json(json_path)

        # pathlib2 object read / modify values and write out
        #TODO:
        #FIXME:find a cleaner way to do this without list indices this should be a dictionary then it's independent of the type of template json
        #FIXME:posted json is a list if it was a dict can move away from indices



        lowRes, highRes = self.calculate_ctfest_range(float(json_to_modify[0]['samplingRate']))
        boxSize = self.calculateBoxSize(float(json_to_modify[0]['samplingRate']), float(json_to_modify[3]['particleSize']))

        # substitutions in  config file (inplace)


        if json_to_modify[3]['object.className'] == "ProtGautomatch":
             json_to_modify[3]['boxSize'] = boxSize
        #
        if json_to_modify[2]['object.className'] == "ProtCTFFind":
             json_to_modify[2]['lowRes'] = lowRes
             json_to_modify[2]['highRes'] = highRes
        #

        shutil.copy(str(json_path), str(workflow))
        self.log.info('copy of %s was completed' %(json_path))




        create_project_args = ['cd', '$SCIPION_HOME;','scipion', '--config $SCIPION_HOME/config/scipion.conf','python',
                               'scripts/create_project.py', project_name, str(workflow), str(workspace_dir)]


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
            self.log.info("I have reached at the point of the lib")
            #sys.exit(0)

            #TODO: kill _the consumer with an exit the controller logic will restart it


        else:
            #kill other processing projects in the visit



            self.on_message(str(project_name), visit_dir)

            self.running_projects.append(project_name)

            self.log.info("%s project  has been added to list of runs "%project_name)

            schedule_project_args = ['cd', '$SCIPION_HOME;', 'scipion','--config $SCIPION_HOME/config/scipion.conf', 'python',
                                     '$SCIPION_HOME/scripts/schedule_project.py', project_name]
            schedule_project_cmd = self._create_prefix_command(schedule_project_args)
            Popen(schedule_project_cmd, cwd=str(workspace_dir), shell=True)


            self.sleeper(2)
            self.log.info("schedule command is ".format(schedule_project_cmd))

            #refresh_project_cmd = self._start_refresh_project(project_name)
            #Popen(refresh_project_cmd, cwd=str(workspace_dir), shell=True)
            # disabled killing because it blocked scipion thread

            return project_name



    def calculateBoxSize(self,samplingRate, particleSize):
        emanBoxSizes = [32, 36, 40, 48, 52, 56, 64, 66, 70, 72, 80, 84, 88,
                        100, 104, 108, 112, 120, 128, 130, 132, 140, 144, 150, 160, 162, 168, 176, 180, 182, 192,
                        200, 208, 216, 220, 224, 240, 256, 264, 288, 300, 308, 320, 324, 336, 338, 352, 364, 384,
                        400, 420, 432, 448, 450, 462, 480, 486, 500, 504, 512, 520, 528, 546, 560, 576, 588,
                        600, 640, 648, 650, 660, 672, 686, 700, 702, 704, 720, 726, 728, 750, 768, 770, 784,
                        800, 810, 840, 882, 896, 910, 924, 936, 972, 980, 1008, 1014, 1020, 1024]


        #convert largest axis/diameter to pixel then add tolerance  factor

        exactBoxSize = int((particleSize * 2) / samplingRate) * 1.2
        for bs in emanBoxSizes:
            if bs >= exactBoxSize:
                return bs

        return 1024


    def calculate_ctfest_range(self,samplingRate):

        if samplingRate < 1:
            return (0.01, 0.35)
        else:
            return (0.03, 0.35)

