import http.client
import hashlib
import urllib
import random
import json
import re
import toml


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


def delete_end_punc(str):  # Delete punctuations at the end of sentences
    punctuation = '，。？！；：,.?!:;'
    return re.sub(re.compile(r'[{}]+$'.format(punctuation)), "", str)


def srt_trans_srt_by_one(input_file, from_lang, to_lang='zh', bi_sub=True):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        output_file = input_file[:-4] + '_trans' + input_file[-4:]
        with open('Output/' + output_file, 'w', encoding='utf-8') as f_out:
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


def srt_trans_srt(input_file, from_lang, to_lang='zh', bi_sub=True, from_lang_top=True):
    """
    Translate the language in the input file into another language
    :param input_file: the srt file to be translated
    :param from_lang: the language of the input file
    :param to_lang: the language of the output file
    :param bi_sub: whether use bi-language subtitle
    :param from_lang_top: whether from_lang subtitles are higher than to_lang subtitles in the output file
    """
    sub_list, format_list = [], []
    name = re.search(re.compile(r'\w+(?=\.)'), input_file).group()
    if bi_sub:
        if from_lang_top:
            output_file = '{}_{}_{}.srt'.format(name, from_lang, to_lang)
        else:
            output_file = '{}_{}_{}.srt'.format(name, to_lang, from_lang)
    else:
        output_file = '{}_{}.srt'.format(name, to_lang)

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
        with open('Output/' + output_file, 'w', encoding='utf-8') as f_out:
            for i, line in enumerate(format_list):
                f_out.write(format_list[i])
                trans_line = delete_end_punc(trans_list[i])
                if bi_sub:
                    if from_lang_top:
                        f_out.write(sub_list[i] + '\n')
                        f_out.write(trans_line + '\n\n')
                    else:
                        f_out.write(trans_line + '\n')
                        f_out.write(sub_list[i] + '\n\n')
                else:
                    f_out.write(trans_line + '\n\n')
        return output_file


def srt_t2ass_t(time):
    time_list = list(map(int, re.split(re.compile('[^0-9]+'), time)))
    ms_s = time_list[3] + time_list[2] * 1000 + time_list[1] * 1000 * 60 + time_list[0] * 1000 * 60 * 60
    ms_e = time_list[7] + time_list[6] * 1000 + time_list[5] * 1000 * 60 + time_list[4] * 1000 * 60 * 60
    ms_sr = int(round(ms_s / 10) * 10)
    ms_er = int(round(ms_e / 10) * 10)
    hour_s = ms_sr // (1000 * 60 * 60)
    hour_e = ms_er // (1000 * 60 * 60)
    minute_s = ms_sr % (1000 * 60 * 60) // (1000 * 60)
    minute_e = ms_er % (1000 * 60 * 60) // (1000 * 60)
    second_s = ms_sr % (1000 * 60 * 60) % (1000 * 60) // 1000
    second_e = ms_er % (1000 * 60 * 60) % (1000 * 60) // 1000
    cs_s = ms_sr % (1000 * 60 * 60) % (1000 * 60) % 1000 // 10
    cs_e = ms_er % (1000 * 60 * 60) % (1000 * 60) % 1000 // 10
    ass_s = '{}:{}:{}.{},'.format(str(hour_s), str(minute_s).zfill(2), str(second_s).zfill(2), str(cs_s).zfill(2))
    ass_e = '{}:{}:{}.{}'.format(str(hour_e), str(minute_e).zfill(2), str(second_e).zfill(2), str(cs_e).zfill(2))
    return ass_s + ass_e


def srt2ass(input_file, language, swap=False):
    """
    Convert srt to ass
    :param input_file:
    :param language: the language of the input srt file. ex. 'zh_en'
    :param swap: whether transform the position of the two subtitle layers in different languages
    """
    config = toml.load('config.toml')
    time_list = []
    output_file = re.search(re.compile(r'[^/]+\.'), input_file).group() + 'ass'

    if len(language) > 2 and re.search(re.compile('zh'), language):
        high_line, low_line = language[:2] + '_line', language[-2:] + '_line'
        high_sub_list, low_sub_list = [], []
        with open(input_file, 'r', encoding='utf-8') as f_in:
            sub_flag = 0
            for line in f_in:
                if re.search(re.compile(r'^\d*\n$'), line):
                    continue
                elif re.search(re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}'), line) and not sub_flag:
                    time_list.append(line.strip())
                    sub_flag = 1
                elif sub_flag == 1:
                    high_sub_list.append(line)
                    sub_flag = 2
                elif sub_flag == 2:
                    low_sub_list.append(line)
                    sub_flag = 0
                else:
                    print('Unidentified line: {}'.format(line))
        if not len(time_list) == len(high_sub_list) == len(low_sub_list):
            print('Length not match!')
        else:
            with open('Output/' + output_file, 'w', encoding='utf-8') as f_out:
                if language == 'zh_en' or language == 'en_zh':
                    if swap:
                        language = language[-2:] + '_' + language[:2]
                    f_out.write(config[language + '_ass']['header'] + '\n')
                    for i, line in enumerate(time_list):
                        ass_t = srt_t2ass_t(time_list[i])
                        ass_t_p = re.compile(r'\d+:\d{2}:\d{2}.\d{2},\d+:\d{2}:\d{2}.\d{2}')
                        high_sub = re.sub(ass_t_p, ass_t, config[language + '_ass'][high_line]) + high_sub_list[i]
                        low_sub = re.sub(ass_t_p, ass_t, config[language + '_ass'][low_line]) + low_sub_list[i]
                        if swap:
                            f_out.write(low_sub)
                            f_out.write(high_sub)
                        else:
                            f_out.write(high_sub)
                            f_out.write(low_sub)


def srt_trans_ass(input_file, from_lang, to_lang='zh', bi_sub=True, from_lang_top=True):
    trans = srt_trans_srt(input_file, from_lang, to_lang, bi_sub, from_lang_top)
    language = re.search(re.compile(r'(_[a-z]{2}){1,2}(?=\.)'), trans).group()[1:]
    srt2ass(trans, language)


input_srt = 'D:/Category/Video/ZBrush 2020从入门到精通全方位训练课ZBrush 2020 Essential Training/002 - Preparing for this course.srt'
srt2ass(input_srt, 'zh_en', swap=True)
# srt_trans_srt(input_srt)
# input_srt = 'Output/16_trans.srt'
# srt2ass(input_srt, 'en_zh')
