import configparser
import os
import re

sentence = "검둥이가 가오를 잡네 개판 에 공갈 치네"
cmplan_kwd_dic = {'개판': '2', '가오': '2', '검둥이': '2', '공갈': '2', '깡통': '2'}

config_parser = configparser.RawConfigParser()
CURR_DIR = os.getcwd()
config_file_path = CURR_DIR +'/conf/b2b_dev_complain_keyword.conf'
config_parser.read(config_file_path)
HOST = config_parser.get('postgres-info', 'POSTGRE_HOST')
PORT = config_parser.get('postgres-info', 'POSTGRE_PORT')
ID = config_parser.get('postgres-info', 'POSTGRE_ID')
PW = config_parser.get('postgres-info', 'POSTGRE_PW')
DB = config_parser.get('postgres-info', 'POSTGRE_DB')
COMPLAIN_KEYWORD_DIC = config_parser.get('table-info', 'COMPLAIN_KEYWORD_DIC')
print("COMPLAIN_KEYWORD_DIC: {}".format(COMPLAIN_KEYWORD_DIC))

if __name__ == '__main__':
    extract_keyword = {}
    win_size = 3
    for dic in cmplan_kwd_dic:
        count = len(re.findall(dic, sentence))
        if count > 0:
            extract_keyword[dic] = count
    print("sentenct: {}".format(sentence))
    print("extract_keyword: {}".format(extract_keyword))

    keyword_list = []
    for key, item in extract_keyword.items():
        keyword_dict = {}
        keyword_dict['keyword'] = key
        keyword_dict['count'] = item
        keyword_list.append(keyword_dict)

    result_dict = {}
    result_dict["complain_keyword_list"] = keyword_list
    print("result_dict: {}".format(result_dict))

    # result = dict(sorted(extract_keyword.items(), key=lambda item: item[1], reverse=True)[:int(win_size)])
    # print("result: {}".format(result))