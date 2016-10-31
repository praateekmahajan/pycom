WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql://userpycom:passw0rd@localhost/pycomm'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
REDIS_URL = "redis://localhost:6379/0"

OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '175010479623525',
        'secret': 'fc4269b44ad673084cd6ca3970c049bb'
    }
}
