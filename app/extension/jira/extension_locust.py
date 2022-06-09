import random
import re
from locustio.jira.requests_params import Login, BrowseIssue, CreateIssue, SearchJql, ViewBoard, BrowseBoards, \
    BrowseProjects, AddComment, ViewDashboard, EditIssue, ViewProjectSummary, jira_datasets
from locustio.common_utils import jira_measure, fetch_by_re, timestamp_int, generate_random_string, TEXT_HEADERS, \
    ADMIN_HEADERS, NO_TOKEN_HEADERS, RESOURCE_HEADERS, init_logger, raise_if_login_failed

from util.conf import JIRA_SETTINGS
import uuid

logger = init_logger(app_type='jira')
jira_dataset = jira_datasets()
FIRST_CONNECTOR = JIRA_SETTINGS.ifaws_connector_id

def app_specific_action_invoke_aws_api_action(locust):
    params = CreateIssue()
    # NOTE: Can't use the random project choice here, as this would need adjustments of all used workflows, hence pinnig just one well known
    # project = random.choice(jira_dataset['projects'])
    # TODO: Adjust/verify - must be a valid project, and the one with the workflow adjusted to use our AAWS action
    project = ["VLLR","10359"]
    project_id = project[1]

    # NOTE: Copied quick create and kept it s execution, just not measuring it, to ensureside effects needed by the create test below
    # @jira_measure('locust_create_issue:open_quick_create')
    def create_issue_open_quick_create():
        raise_if_login_failed(locust)

        # 200 /secure/QuickCreateIssue!default.jspa?decorator=none
        r = locust.post('/secure/QuickCreateIssue!default.jspa',
                        json={'atlassian.xsrf.token': locust.session_data_storage["token"]},
                        headers=ADMIN_HEADERS, catch_response=True)

        content = r.content.decode('utf-8')
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        issue_type = fetch_by_re(params.issue_type_pattern, content)
        resolution_done = fetch_by_re(params.resolution_done_pattern, content)
        fields_to_retain = re.findall(params.fields_to_retain_pattern, content)
        custom_fields_to_retain = re.findall(params.custom_fields_to_retain_pattern, content)

        issue_body_params_dict = {'atl_token': atl_token,
                                  'form_token': form_token,
                                  'issue_type': issue_type,
                                  'project_id': project_id,
                                  'resolution_done': resolution_done,
                                  'fields_to_retain': fields_to_retain,
                                  'custom_fields_to_retain': custom_fields_to_retain
                                  }

        if not ('"id":"project","label":"Project"' in content):
            logger.error(f'{params.err_message_create_issue}: {content}')
        assert '"id":"project","label":"Project"' in content, params.err_message_create_issue

        # 205 /rest/quickedit/1.0/userpreferences/create
        locust.post('/rest/quickedit/1.0/userpreferences/create',
                    json=params.user_preferences_payload,
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 210 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("210"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        locust.session_data_storage['issue_body_params_dict'] = issue_body_params_dict

    create_issue_open_quick_create()

    @jira_measure("locust_app_invoke_aws_api_action")
    def create_issue_submit_form():
        raise_if_login_failed(locust)
        issue_body = params.prepare_issue_body(locust.session_data_storage['issue_body_params_dict'],
                                               user=locust.session_data_storage["username"])

        # 215 /secure/QuickCreateIssue.jspa?decorator=none
        r = locust.post('/secure/QuickCreateIssue.jspa?decorator=none',
                        json={'atlassian.xsrf.token': locust.session_data_storage["token"]},
                        params=issue_body,
                        headers=ADMIN_HEADERS,
                        catch_response=True)

        # 220 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("220"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        content = r.content.decode('utf-8')
        if '"id":"project","label":"Project"' not in content:
            logger.error(f'{params.err_message_create_issue}: {content}')
        assert '"id":"project","label":"Project"' in content, params.err_message_create_issue
        issue_key = fetch_by_re(params.create_issue_key_pattern, content)
        logger.locust_info(f"{params.action_name}: Issue {issue_key} was successfully created")

    create_issue_submit_form()