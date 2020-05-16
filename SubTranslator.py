import http.client
import hashlib
import urllib
import random
import json
import re


def translate(q, from_lang='auto', to_lang='zh'):
    app_id = '20200108000373970'  # 填写你的appid
    secret_key = 'wovG1CuvOYi9DOYKJPgM'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'
    salt = random.randint(32768, 65536)
    sign = app_id + q + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + app_id + '&q=' + urllib.parse.quote(
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
        return dst

    except Exception as e:
        print(e)

    finally:
        if httpClient:
            httpClient.close()


def srt2srt(input_file, from_lang='auto', to_lang='zh'):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        output_file = input_file[:-4] + '_trans' + input_file[-4:]
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                pattern = re.compile('^\d*$|\d{2}:\d{2}:\d{2},\d{3}|\n')
                if re.match(pattern, line):
                    f_out.write(line)
                else:
                    line_trans = translate(line.strip(), from_lang, to_lang)
                    print(line_trans)
                    f_out.write(line_trans + '\n')


input_srt = '25 - Applying Colors and Patterns.srt'
srt2srt(input_srt)
