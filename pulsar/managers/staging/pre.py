"""
"""
from pulsar.client.action_mapper import from_dict
import logging
import time

log = logging.getLogger(__name__)


def preprocess(job_directory, setup_actions, action_executor, object_store=None):
    timing_start = time.time()

    for setup_action in setup_actions:
        name = setup_action["name"]
        input_type = setup_action["type"]
        action = from_dict(setup_action["action"])
        if getattr(action, "inject_object_store", False):
            action.object_store = object_store
        path = job_directory.calculate_path(name, input_type)
        description = "Staging %s '%s' via %s to %s" % (input_type, name, action, path)
        log.debug(description)
        action_executor.execute(lambda: action.write_to_path(path), "action[%s]" % description)

    preprocessing_time = time.time() - timing_start
    job_directory.store_metadata("preprocessing_time", preprocessing_time)
    log.debug("Files processed in %fs" % preprocessing_time)
    # To work with custom staging_time plugin
    with open(job_directory.metadata_directory() + "/__instrument_staging_time_preprocessing_time", "w+") as txt:
        txt.write(str(preprocessing_time))


__all__ = ('preprocess',)
