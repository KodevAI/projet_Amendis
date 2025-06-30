# class Config:
#     # Remplace les éléments de l'URI par tes propres informations
#     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345@localhost/amendis'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SECRET_KEY = 'secretkey'
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@db:3306/amendis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'secretkey')
