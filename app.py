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

if __name__ == '__main__':
    app.run(debug=True)
