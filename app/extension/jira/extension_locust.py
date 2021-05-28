import re
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='jira')
FIRST_CONNECTOR = "add4aa6b-2b7f-473d-ab7b-1d2bcb76830e"

@run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):
    
    @jira_measure("locust_app_api_get_temporary_credentials")
    def get_temporary_credentials():
        path = "/rest/identity-federation-for-aws/2.2/connectors/" + FIRST_CONNECTOR + "/credentials"
        r = locust.get(path, catch_response=True)  # call app-specific GET endpoint
        
        assert r.status_code == 200, f"expected GET .../credentials 200, got {r.status_code}"
        
    get_temporary_credentials()
