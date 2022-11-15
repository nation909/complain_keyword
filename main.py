# -- coding: utf-8 --
import configparser
import json
import logging.config
import os
from configparser import ConfigParser

import psycopg2 as pg2
from flask import Flask, jsonify, request
from flask_caching import Cache

from logging_conf import LOGGING_CONFIG
from src.cmplan import complain_keyword
from version import VERSION

# Config
CURR_DIR = os.getcwd()
config = ConfigParser()
config.read(CURR_DIR + '/config.ini')
target = config.get('server', 'target', fallback='dev')

config_file_path = CURR_DIR + '/conf/b2b_{}_complain_keyword.conf'.format(target)
config_parser = configparser.RawConfigParser()
config_parser.read(config_file_path)
HOST = config_parser.get('postgres-info', 'POSTGRES_HOST')
PORT = config_parser.get('postgres-info', 'POSTGRES_PORT')
ID = config_parser.get('postgres-info', 'POSTGRES_ID')
PW = config_parser.get('postgres-info', 'POSTGRES_PW')
DB = config_parser.get('postgres-info', 'POSTGRES_DB')
COMPLAIN_KEYWORD_DIC = config_parser.get('table-info', 'COMPLAIN_KEYWORD_DIC')

# Flask & Flask_cache
app = Flask(__name__)  # Flask에 객체를 만들고
app.config.from_pyfile("conf/flask-caching.conf")
app.config['JSON_AS_ASCII'] = False  # jsonify return 시 한글이 ascii 값으로 전달되어 ascii 설정 off 함
cache = Cache(app)  # cache 객체에 flask 객체를 입혀서 처리하는 방식

# LOG
logging.config.dictConfig(LOGGING_CONFIG)


@cache.cached(key_prefix="update_cmplan_kwd")
def cmplan_kwd_reload():
    conn = pg2.connect(host=HOST, user=ID, password=PW, database=DB, port=PORT)
    curs = conn.cursor()
    sql = "select keyword, weight from {} where use_yn = 'Y'".format(COMPLAIN_KEYWORD_DIC)
    curs.execute(sql)
    cmplan_kwd_dic = {i[0]: i[1] for i in curs.fetchall()}
    conn.close()
    return cmplan_kwd_dic


@app.route('/assist/cmplan', methods=['POST'])
def cmplan_kwd():
    json_data = json.loads(request.data)
    logging.debug("json_data: %s", json_data)
    try:
        interface_id = json_data['interfaceId']
        if interface_id == '2000':
            cmplan_kwd_dic = cmplan_kwd_reload()
            logging.debug("dictionary data: %s", cmplan_kwd_dic)

            stt_sentence = json_data['sttSentence']
            result = complain_keyword.extract_complain_keyword(stt_sentence, cmplan_kwd_dic)
        else:
            return {"result": "failed", "message": "Complain keyword api Error"}
    except Exception as e:
        logging.error("Complain Keyword Method Error: {}".format(e))
    return jsonify(result)


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    logging.debug("pong")
    return "pong"


if __name__ == '__main__':
    logging.info("complain keyword module start version: %s", VERSION)
    app.run('0.0.0.0', port=9999, debug=True)
