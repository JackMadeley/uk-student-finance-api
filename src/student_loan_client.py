from requests import Session
import logging
from bs4 import BeautifulSoup as bs


class StudentLoanClient:

    def __init__(self):
        self.login_page = "https://logon.slc.co.uk/welcome/secured/login"
        self.overview_page = "https://www.manage-student-loan-balance.service.gov.uk/ors/account-overview/secured/summary"
        self.session = Session()

    def login(self, username: str, password: str, secret_answer: str) -> None:
        """
        A function to login to the service's page and obtain a valid session
        :param username: Login email address
        :param password: Login password
        :param secret_answer: Answer to secret question
        :return: None
        """
        with self.session as s:
            login_get_request = s.get(url=self.login_page)
            if login_get_request.status_code == 200:
                login_page_content = bs(login_get_request.content, "lxml")
                try:
                    _csrf = login_page_content.select_one("input[name=_csrf]")["value"]
                except Exception:
                    raise Exception("Could not find _csrf token")
                try:
                    lt = login_page_content.select_one("input[name=lt]")["value"]
                except Exception:
                    raise Exception("Could not find lt in request page")
                try:
                    execution = login_page_content.select_one("input[name=execution]")["value"]
                except Exception:
                    raise Exception("Could not find execution in request page")
                try:
                    _eventId = login_page_content.select_one("input[name=_eventId]")["value"]
                except Exception:
                    raise Exception("Could not find _eventId in request page")
                step_1_form_data = {
                    "_csrf": _csrf,
                    "userId": username,
                    "password": password,
                    "lt": lt,
                    "execution": execution,
                    "_eventId": _eventId,
                    "continue-button": ""
                }
                step_1_post_request = s.post(url=self.login_page, data=step_1_form_data, cookies=s.cookies)
                if step_1_post_request.status_code == 200:
                    step_2_form_data = {
                        "_csrf": _csrf,
                        "secretAnswer": secret_answer,
                        "continue-button": ""
                    }
                    step_2_post_request = s.post(url=step_1_post_request.url, data=step_2_form_data,
                                                 cookies=s.cookies, verify=False)
                    if step_2_post_request.status_code == 200:
                        self.session.cookie = step_2_post_request.cookies
                    else:
                        logging.critical(f"Login secret page post request failed, status code {step_2_post_request.status_code}")
                else:
                    logging.critical(f"Login page post request failed, status code {step_1_post_request.status_code}")
            else:
                logging.critical(f"Unable to load login url {self.login_page}. Status code {login_get_request.status_code}")

    def get_summary(self) -> dict:
        """
        A function to get account overview information such as account balance, current interest rate, current year,
        salary repayments, direct repayments and interest added.
        :return: A dict object with the account summary
        """
        output = {}
        with self.session as s:
            overview_page = s.post(url=self.overview_page, cookies=s.cookies)
            if overview_page.status_code == 200:
                overview_context = bs(overview_page.content, "lxml")
                try:
                    para = overview_context.find("p", {"id": "balanceId_1"})
                    split_para = para.text.split("\n")
                    figure_str = [x for x in split_para if x.strip().startswith("£")][0].strip()
                    figure = float(figure_str.replace("£", "").replace(",", ""))
                    output["balance"] = figure
                except AttributeError as ex:
                    logging.error(f"Could not find balance attribute in summary page, {str(ex)}")
                try:
                    para = overview_context.find("p", {"id": "interestAsOfDateId-1"})
                    split_para = para.text.split("\n")
                    interest_rate_str = [x for x in split_para if x.strip().endswith("%")][0].strip()
                    interest_rate = float(interest_rate_str.replace("%", "")) / 100
                    output["interest rate"] = interest_rate
                except AttributeError as ex:
                    logging.error(f"Could not find interest rate attribute in summary page, {str(ex)}")
                try:
                    header = overview_context.find("h2", {"id": "academicYearSummaryId-1"})
                    current_year = str(header.contents[0]).replace("summary", "").strip()
                    output["current year"] = current_year
                except AttributeError as ex:
                    logging.error(f"Could not find current year attribute in summary page, {str(ex)}")
                try:
                    td = overview_context.find("td", {"id": "salaryRepaymentAmountId-1"})
                    amount_str = str(td.contents[0]).replace("£", "").replace(",", "")
                    output["salary repayments"] = float(amount_str)
                except AttributeError as ex:
                    logging.error(f"Could not find salary repayments attribute in summary page, {str(ex)}")
                try:
                    td = overview_context.find("td", {"id": "directRepaymentAmountId-1"})
                    amount_str = str(td.contents[0]).replace("£", "").replace(",", "")
                    output["direct repayments"] = float(amount_str)
                except AttributeError as ex:
                    logging.error(f"Could not find direct repayments attribute in summary page, {str(ex)}")
                try:
                    td = overview_context.find("td", {"id": "interestAddedAmountId-1"})
                    amount_str = str(td.contents[0]).replace("£", "").replace(",", "")
                    output["interest added"] = float(amount_str)
                except AttributeError as ex:
                    logging.error(f"Could not find interest added attribute in summary page, {str(ex)}")
            else:
                logging.error(f"Could not load overview page, status code {overview_page.status_code}")
        return output
