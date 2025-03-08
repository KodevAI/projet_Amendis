class Config:
    # Remplace les éléments de l'URI par tes propres informations
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345@localhost/amendis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secretkey'
