import pathlib

try:
    import zoo
except ImportError:

    class ZooStub(object):
        def __init__(self):
            self.SERVICE_SUCCEEDED = 3
            self.SERVICE_FAILED = 4

        def update_status(self, conf, progress):
            print(f"Status {progress}")

        def _(self, message):
            print(f"invoked _ with {message}")

    zoo = ZooStub()

import os
import sys
import traceback
import yaml
from loguru import logger
from zoo_calrissian_runner import ExecutionHandler, ZooCalrissianRunner

logger.remove()
logger.add(sys.stderr, level="INFO")

class SimpleExecutionHandler(ExecutionHandler):
    def __init__(self, conf):
        super().__init__()
        self.conf = conf

    def pre_execution_hook(self):
        
        logger.info("Pre execution hook")

    def post_execution_hook(self, log, output, usage_report, tool_logs):

        logger.info("Post execution hook")
       
    def get_pod_env_vars(self):

        logger.info("get_pod_env_vars")

        env_vars = {"A": "1", "B": "2"}

        return env_vars

    def get_pod_node_selector(self):

        logger.info("get_pod_node_selector")

        node_selector = {}

        return node_selector
    
    def get_additional_parameters(self):

        logger.info("get_additional_parameters")

        additional_parameters = {
            "s3_bucket": "results",
            "sub_path": self.conf["lenv"]["usid"],
            "region_name": "us-east-1",
            "aws_secret_access_key": "test",
            "aws_access_key_id": "test",
            "endpoint_url": "http://localstack:4566",
        }

        logger.info(f"additional_parameters: {additional_parameters.keys()}")

        return additional_parameters

    def handle_outputs(self, log, output, usage_report, tool_logs):
        """
        Handle the output files of the execution.

        :param log: The application log file of the execution.
        :param output: The output file of the execution.
        :param usage_report: The metrics file.
        :param tool_logs: A list of paths to individual workflow step logs.

        """
        try:
            logger.info("handle_outputs")

            self.conf['main']['tmpUrl']=self.conf['main']['tmpUrl'].replace("temp/",self.conf["auth_env"]["user"]+"/temp/")
            services_logs = [
                {
                    "url": os.path.join(self.conf['main']['tmpUrl'],
                                        f"{self.conf['lenv']['Identifier']}-{self.conf['lenv']['usid']}",
                                        os.path.basename(tool_log)),
                    "title": f"Tool log {os.path.basename(tool_log)}",
                    "rel": "related",
                }
                for tool_log in tool_logs
            ]
            for i in range(len(services_logs)):
                okeys = ["url", "title", "rel"]
                keys = ["url", "title", "rel"]
                if i > 0:
                    for j in range(len(keys)):
                        keys[j] = keys[j] + "_" + str(i)
                if "service_logs" not in self.conf:
                    self.conf["service_logs"] = {}
                for j in range(len(keys)):
                    self.conf["service_logs"][keys[j]] = services_logs[i][okeys[j]]

            self.conf["service_logs"]["length"] = str(len(services_logs))
            logger.info(f"service_logs: {self.conf['service_logs']}")

        except Exception as e:
            logger.error("ERROR in handle_outputs...")
            logger.error(traceback.format_exc())
            raise(e)

    def get_secrets(self):
        return {}

def water_bodies(conf, inputs, outputs): # noqa

    try:
        with open(
            os.path.join(
                pathlib.Path(os.path.realpath(__file__)).parent.absolute(),
                "app-package.cwl",
            ),
            "r",
        ) as stream:
            cwl = yaml.safe_load(stream)

        execution_handler = SimpleExecutionHandler(conf=conf)

        runner = ZooCalrissianRunner(
            cwl=cwl,
            conf=conf,
            inputs=inputs,
            outputs=outputs,
            execution_handler=execution_handler,
        )

        working_dir = os.path.join(conf["main"]["tmpPath"], runner.get_namespace_name())
        os.makedirs(
            working_dir,
            mode=0o777,
            exist_ok=True,
        )
        os.chdir(working_dir)

        exit_status = runner.execute()

        if exit_status == zoo.SERVICE_SUCCEEDED:
            logger.info(f"Setting Collection into output key {list(outputs.keys())[0]}")
            outputs[list(outputs.keys())[0]]["value"] = execution_handler.feature_collection
            return zoo.SERVICE_SUCCEEDED

        else:
            conf["lenv"]["message"] = zoo._("Execution failed")
            logger.error("Execution failed")
            return zoo.SERVICE_FAILED

    except Exception as e:
        
        logger.error("ERROR in processing execution template...")
        logger.error("Try to fetch the tool logs if any...")
        
        try:
            tool_logs = runner.execution.get_tool_logs()
            execution_handler.handle_outputs(None, None, None, tool_logs)
        except Exception as e:
            logger.error(f"Fetching tool logs failed! ({str(e)})")
        
        stack = traceback.format_exc()
        
        logger.error(stack)
        
        conf["lenv"]["message"] = zoo._(f"Exception during execution...\n{stack}\n")
        
        return zoo.SERVICE_FAILED
