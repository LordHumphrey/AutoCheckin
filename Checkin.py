import requests
import os
import yagmail
import json

check_in = os.environ["CHECKIN"]
cookie = os.environ["COOKIE"]

email = os.environ["EMAIL"]
email_password = os.environ["EMAILPASSWORD"]
target_email = os.environ["TARGETEMAIL"]


def main():
    s = requests.Session()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'close',
        'Content-Length': '0',
        'cookie': cookie
    }

    result = s.post(check_in, headers=header)
    result_dict = json.loads(result.content)
    email_message = ""
    for key, value in result_dict.items():
        email_message = email_message + str(key) + ":" + str(value) + " ; "
    send_email(email_message)


def send_email(contents):
    yag = yagmail.SMTP(user=email, password=email_password, host='smtp.office365.com', port=587,
                       smtp_starttls=True, smtp_ssl=False)

    yag.send(target_email, '每日签到', contents)


if __name__ == "__main__":
    main()
