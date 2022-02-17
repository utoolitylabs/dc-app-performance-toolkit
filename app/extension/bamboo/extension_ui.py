import random
import sys

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bamboo.pages.pages import Login, ProjectList
from util.conf import BAMBOO_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    rnd_plan = random.choice(datasets["build_plans"])

    build_plan_id = rnd_plan[1]

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.click_login_button()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    projectlist_page = ProjectList(webdriver)

    @print_timing("selenium_app_ui_connector_menu")
    def measure():
        # NOTE: Kept extensive per line exception detection/logging in case we run into issues again, as it should not matter for normal test execution
        try:
            projectlist_page.go_to()
        except Exception:
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = f"Failed projectlist_page.go_to(): {exc_type.__name__}"
            raise Exception(error_msg, full_exception)
        try:
            projectlist_page.wait_until_clickable((By.ID, "ifaws-aws-resources-link")).click()  # Wait for connector menu trigger
        except Exception:
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = f"Failed projectlist_page.wait_until_clickable(): {exc_type.__name__}"
            raise Exception(error_msg, full_exception)
        try:
            projectlist_page.wait_until_visible((By.CSS_SELECTOR, "a[title='Go to AWS connector configuration page']"))  # Wait for connector menu visible
        except Exception:
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = f"Failed projectlist_page.wait_until_visible(): {exc_type.__name__}"
            raise Exception(error_msg, full_exception)
    measure()
