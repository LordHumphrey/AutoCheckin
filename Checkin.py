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
    def __init__(self, check_in_url, cookie, email):
        self.email = email
        self.session = requests.Session()
        self.check_in_url = check_in_url
        self.cookie = cookie
        self.result_dict = ""
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'close',
            'Content-Length': '0',
            'cookie': cookie
        }

    def get_name(self):
        get_name_url = str(self.check_in_url).replace("/user/checkin", "/user")
        html_content = self.session.get(get_name_url, headers=self.header).content.decode("utf-8")
        return re.findall(r'<title>(.*?)</title>', html_content)[0].replace("&mdash;",
                                                                            "—").replace(
            "用户中心 — ", "") + ": "

    def main(self):
        self.email.email_content += self.get_name()
        result = self.session.post(self.check_in_url, headers=self.header)
        try:
            self.result_dict = json.loads(result.content)
        except JSONDecodeError:
            self.email.email_content += "Cookie失效或者登陆失败"
        else:
            for key, value in self.result_dict.items():
                self.email.email_content = self.email.email_content + str(key) + ":" + str(value) + " ; "
            self.email.email_content += "\n"



if __name__ == "__main__":
    check_in_list = os.environ["CHECKIN"].split(",")
    cookie_list = os.environ["COOKIE"].split(",")
    email = os.environ["EMAIL"]
    email_password = os.environ["EMAILPASSWORD"]
    target_email = os.environ["TARGETEMAIL"]
    email_instance = Email(email, email_password, target_email)

    for check_in, cookie in zip(check_in_list, cookie_list):
        my_heck_in = CheckIn(check_in, cookie, email_instance)
        my_heck_in.main()
        del my_heck_in

    email_instance.send_email()
