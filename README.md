# uk-student-finance-api
A small API client for retrieving information about your student loan from the UK
Student Loan service.

<h2>Motivation</h2>
There is no existing API available to retrieve information about a student loan,
in order to check the current interest rate and balance a user must manually log in which is time consuming.

<h2>Usage</h2>
To get the overview account information:

```python
from uk-student-finance-api.student_loan_client import StudentLoanClient

client = StudentLoanClient()

client.login(username="USERNAME"),
             password="PASSWORD",
             secret_answer="SECRET_ANSWER")

account_summary = client.get_summary()
```

This will return a dict object containing the current balance, current interest rate, current year,
total salary repayments made in the year, total direct repayments made in the year and the total interest
added in the year.

<h2>Authentication</h2>
The service operates on a two-phase login process, step one requests your username
and password, then step two requests your secret question answer.
\n
The only sort of authentication required is the CSRF token that is obtained
when the user first accesses the login page.
\n
This token does not change between step one and step two, and must be provided to both POST requests.

<h2>Contributing</h2>
Pull requests are welcomed. Currently, the client only retrieves the account overview
information.

