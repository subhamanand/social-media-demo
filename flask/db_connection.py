import pymysql
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

def get_db_conection():
    host = config['DBINFO']['host']
    user = config['DBINFO']['user']
    password = config['DBINFO']['password']
    database = config['DBINFO']['database']
    db = pymysql.connect(
        host=host, user=user, passwd=password, db=database)
    return db