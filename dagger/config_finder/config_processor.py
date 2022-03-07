import logging
from os import environ
from os.path import join, relpath, splitext
from mergedeep import merge

import yaml
from envyaml import EnvYAML
from dagger.config_finder.config_finder import ConfigFinder
from dagger.pipeline.pipeline import Pipeline
from dagger.pipeline.task_factory import TaskFactory

import dagger.conf as conf


_logger = logging.getLogger("configFinder")
DAG_DIR = join(environ.get("AIRFLOW_HOME", "./"), "dags")


class ConfigProcessor:
    def __init__(self, config_finder: ConfigFinder):
        self._config_finder = config_finder
        self._task_factory = TaskFactory()

    @staticmethod
    def _load_yaml(yaml_path):
        with open(yaml_path, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                _logger.exception("Couldn't read config file {}", yaml_path, exc)
                exit(1)
        return config

    @staticmethod
    def localize_params(config):
        env_dependent_params = config.get("environments", {}).get(conf.ENV, {})
        if env_dependent_params.get("deactivate"):
            return None
        merge(config, env_dependent_params)
        return config

    def process_pipeline_configs(self):
        configs = self._config_finder.find_configs()
        pipelines = []

        for pipeline_config in configs:
            pipeline_name = relpath(pipeline_config.directory, DAG_DIR).replace(
                "/", "-"
            )
            config_path = join(pipeline_config.directory, pipeline_config.config)

            _logger.info("Processing config: %s", config_path)
            config_dict = EnvYAML(config_path).export()
            config_dict = self.localize_params(config_dict)
            pipeline = Pipeline(pipeline_config.directory, config_dict)

            for task_config in pipeline_config.job_configs:
                task_name = splitext(task_config.config)[0]
                task_config_path = join(pipeline_config.directory, task_config.config)

                _logger.info("Processing task config: %s", task_config_path)
                task_config = EnvYAML(task_config_path).export()
                task_config = self.localize_params(task_config)
                if task_config:
                    task_type = task_config["type"]
                    pipeline.add_task(
                        self._task_factory.create_task(
                            task_type, task_name, pipeline_name, pipeline, task_config
                        )
                    )
                else:
                    _logger.info(f"{task_name} job is disabled in {conf.ENV} environment")

            pipelines.append(pipeline)

        return pipelines
