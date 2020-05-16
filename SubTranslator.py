import http.client
import hashlib
import urllib
import random
import json


def translate(q, from_lang='auto', to_lang='zh'):
    app_id = '20200108000373970'  # 填写你的appid
    secret_key = 'wovG1CuvOYi9DOYKJPgM'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'
    salt = random.randint(32768, 65536)
    sign = app_id + q + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?app_id=' + app_id + '&q=' + urllib.parse.quote(
        q) + '&from=' + from_lang + '&to=' + to_lang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        dst = result["trans_result"][0]["dst"]
        print(dst)

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


