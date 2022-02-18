import re
from locustio.common_utils import init_logger, bamboo_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='bamboo')

logger = init_logger(app_type='bamboo')
FIRST_CONNECTOR = "f70a97a6-5362-4dec-8fbc-630ee925d1af"

# NOTE: Quite a deviation from the original sample, but that would not cater for multiple custom actions without changes to dc toolkit core logic,
# hence starting with on custom action invoking multiple measurements in itself (to be revised if results are not satisfactory)
# @run_as_specific_user(username='admin', password='admin')
@bamboo_measure("locust_app_api_get_temporary_credentials")
def app_specific_action_get_temporary_credential(locust):
    
    # logger.info(f"'get_temporary_credentials() called ...")
    path = "/rest/identity-federation-for-aws/2.2/connectors/" + FIRST_CONNECTOR + "/credentials"
    r = locust.get(path, catch_response=True)  # call app-specific GET endpoint
    logger.info(f"'... locust.get() returned status code {r.status_code} ...")
    
    assert r.status_code == 200, f"expected GET .../credentials 200, got {r.status_code}"
    
    
@bamboo_measure("locust_app_api_get_ecr_credentials")
def app_specific_action_get_ecr_credential(locust):
    # logger.info(f"'get_ecr_credentials() called ...")
    path = "/rest/identity-federation-for-aws/2.2/connectors/" + FIRST_CONNECTOR + "/credentials"
    r = locust.get(path, catch_response=True)  # call app-specific GET endpoint
    logger.info(f"'... locust.get() returned status code {r.status_code} ...")
    
    assert r.status_code == 200, f"expected GET .../credentials 200, got {r.status_code}"
