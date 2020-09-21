from json import JSONDecodeError
import requests
import os
import yagmail
import json
import re


class Email:
    def __init__(self, email, email_password, target_email):
        self.email = email
        self.email_password = email_password
        self.target_email = target_email
        self.email_content = ""

    def send_email(self):
        yag = yagmail.SMTP(user=email, password=email_password, host='smtp.office365.com', port=587,
                           smtp_starttls=True, smtp_ssl=False)
        yag.send(self.target_email, '每日签到', self.email_content)


class CheckIn:
    def __init__(self, login_url, account, password, email):
        self.login_url = login_url
        self.password = password
        self.account = account
        self.result_dict = ""
        self.session = requests.Session()
        self.email = email
        self.checkin_url = str(login_url).replace("/auth/login", "/user/checkin")
        self.login_data = {
            "email": account,
            "passwd": password
        }
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'close',
            'Content-Length': '0',
        }

    def login(self):
        self.session.post(self.login_url, headers=self.header, data=self.login_data)

    def get_name(self):
        get_name_url = str(self.checkin_url).replace("/user/checkin", "/user")
        html_content = self.session.get(get_name_url, headers=self.header).content.decode("utf-8")
        return re.findall(r'<title>(.*?)</title>', html_content)[0].replace("&mdash;",
                                                                            "—").replace(
            "用户中心 — ", "") + ": "

    def main(self):
        self.login()
        self.email.email_content += self.get_name()
        result = self.session.post(self.checkin_url, headers=self.header)
        try:
            self.result_dict = json.loads(result.content)

        except JSONDecodeError:
            self.email.email_content += "Cookie失效或者登陆失败！"
        else:
            for key, value in self.result_dict.items():
                self.email.email_content = self.email.email_content + str(key) + ":" + str(value) + " ; "
        self.email.email_content += "\n"


class WebsiteAccount:
    def __init__(self, url, account, password):
        self.url = url
        self.account = account
        self.password = password


if __name__ == "__main__":
    login_url_list = os.environ["LOGIN_URL"].split(",")
    account_list = os.environ["ACCOUNT"].split(",")
    password_list = os.environ["PASSWORD"].split(",")
    email = os.environ["EMAIL"]
    email_password = os.environ["EMAILPASSWORD"]
    target_email = os.environ["TARGETEMAIL"]

    email_instance = Email(email, email_password, target_email)

    for login_url, account, password in zip(login_url_list, account_list, password_list):
        my_heck_in = CheckIn(login_url, account, password, email_instance)
        my_heck_in.main()
        del my_heck_in

    email_instance.send_email()
