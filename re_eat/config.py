import os
import ConfigParser
from PyQt4.QtGui import QInputDialog

config_dir = os.path.expanduser('~/.re-eat/')
config_file = os.path.join(config_dir, 'config.ini')

config = ConfigParser.ConfigParser()
config.read(config_file)

def database_url():
    try:
        return config.get('DEFAULT', 'database')
    except ConfigParser.NoOptionError:
        url, _ = QInputDialog.getText(None, 'Database selection',
                                      'Please enter the url to the database',
                                      text='sqlite:///%s'%os.path.join(config_dir, 'db.sqlite'))
        config.set('DEFAULT', 'database', url)
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
        with open(config_file, 'wb') as configfile:
            config.write(configfile)
        return url