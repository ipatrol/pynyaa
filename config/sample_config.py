
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://nyaa:nyaa@localhost/nyaa'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

# >>> letters = string.digits + string.ascii_letters + string.punctuation
# >>> ''.join(random.choice(letters) for _ in range(100))
SECRET_KEY = 'changeme'
