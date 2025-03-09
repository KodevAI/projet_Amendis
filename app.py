from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Initialiser SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Charger la configuration depuis config.py
    app.config.from_object('config.Config')

    # Initialiser SQLAlchemy avec l'app Flask
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Créer les tables si elles n'existent pas

    return app

# Créer l'application Flask
app = create_app()

# Page d'accueil
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/avisdoffre')
def avisdoffre():
    return render_template('avisdoffre.html')

@app.route('/marchesattribues')
def marchesattribues():
    return render_template('marchesattribues.html')

@app.route('/demaprogsoc')
def demaprogsoc():
    return render_template('demaprogsoc.html')

@app.route('/reglmarch')
def reglmarch():
    return render_template('reglmarch.html')

@app.route('/reglmarch/documents')
def documents():
    return render_template('documents.html')

@app.route('/proginvest')
def proginvest():
    return render_template('proginvest.html')

@app.route('/contacternous')
def contacternous():
    return render_template('contacternous.html')

if __name__ == '__main__':
    app.run(debug=True)
