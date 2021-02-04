import configparser

config = configparser.ConfigParser()
config.read('settings.ini')



DATABASES = {
    'user': config['DBSETTINGS']['user'],
    'passwd': config['DBSETTINGS']['passwd'],
    'db_host': config['DBSETTINGS']['db_host'],
    'db_port': config['DBSETTINGS']['db_port'],
    'db_name': config['DBSETTINGS']['db_name'],
    'charset': config['DBSETTINGS']['charset'],
}

JWT = {
    'key': config['JWTSETTINGS']['key']
}
