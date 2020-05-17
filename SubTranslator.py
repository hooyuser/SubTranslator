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


def srt2srt_by_one(input_file, from_lang='auto', to_lang='zh', bi_sub=True):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        output_file = input_file[:-4] + '_trans' + input_file[-4:]
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                pattern = re.compile('^\d*$|\d{2}:\d{2}:\d{2},\d{3}')
                if re.match(pattern, line):
                    f_out.write(line)
                else:
                    line_trans = translate(line.strip(), from_lang, to_lang)
                    print(line_trans)
                    if bi_sub:
                        f_out.write(line)
                    f_out.write(line_trans + '\n')


def srt2srt(input_file, from_lang='auto', to_lang='zh', bi_sub=True):
    sub_list, format_list = [], []
    output_file = input_file[:-4] + '_trans' + input_file[-4:]
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            if re.match(re.compile(r'^\d+\n$'), line):
                format_list.append(line)
            elif re.match(re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}'), line):
                format_list[-1] += line
            elif line == '\n':
                continue
            else:
                sub_list.append(line.strip())
    sep = '. one. '
    text = sep.join(sub_list)
    text_trans = translate(text, from_lang, to_lang)
    trans_list = text_trans.split('一个。')

    if not len(format_list) == len(sub_list) == len(trans_list):
        print('Length not match!')
    else:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for i, line in enumerate(format_list):
                f_out.write(line)
                if bi_sub:
                    f_out.write(sub_list[i] + '\n')
                punctuation = '，。？！；：,.?!:;'  # Delete punctuations at the end of sentences
                trans_line = re.sub(re.compile(r'[{}]+$'.format(punctuation)), "", trans_list[i])
                f_out.write(trans_line + '\n\n')


input_srt = '07.srt'
srt2srt(input_srt)
