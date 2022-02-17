from locust import HttpUser, task, between
from extension.bamboo.extension_locust import app_specific_action_get_temporary_credential, app_specific_action_get_ecr_credential
from locustio.bamboo.http_actions import locust_bamboo_login
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from util.conf import BAMBOO_SETTINGS

config = LocustConfig(config_yml=BAMBOO_SETTINGS)


class BambooBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        locust_bamboo_login(self)

    @task(config.percentage('standalone_extension_locust'))
    def custom_action_get_temporary_credential(self):
        # KLUDGE: The terraform based Bamboo setup uses the default 30min session timeout,
        # and the locust instrumentation of the toolkit does not cater for the thus unavoidable 403/401 responses
        # starting after 30min - this should be fixed either in the Bamboo test instance itself,
        # or by improved login/-out handling in the toolkit, but to get test results for now,
        # we accept the overhead of a dedicated login per custom action REST call
        locust_bamboo_login(self)
        app_specific_action_get_temporary_credential(self)

    @task(config.percentage('standalone_extension_locust'))
    def custom_action_get_ecr_credential(self):
        # KLUDGE: The terraform based Bamboo setup uses the default 30min session timeout,
        # and the locust instrumentation of the toolkit does not cater for the thus unavoidable 403/401 responses
        # starting after 30min - this should be fixed either in the Bamboo test instance itself,
        # or by improved login/-out handling in the toolkit, but to get test results for now,
        # we accept the overhead of a dedicated login per custom action REST call
        locust_bamboo_login(self)
        app_specific_action_get_ecr_credential(self)


class BambooUser(HttpUser):
    host = BAMBOO_SETTINGS.server_url
    tasks = [BambooBehavior]
    wait_time = between(0, 0)
