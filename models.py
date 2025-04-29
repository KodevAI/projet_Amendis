from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # password123
    role = db.Column(db.Enum('admin', 'user'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class Fournisseur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # frss123
    entreprise = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    date_inscription = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class AppelOffre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date_lancement = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_limite = db.Column(db.DateTime, nullable=False)
    budget_estime = db.Column(db.Numeric(15,2), nullable=False)
    statut = db.Column(db.Enum('Ouvert', 'Fermé', 'Attribué'), default='Ouvert')
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='appels_offres')

class Offre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appel_offre_id = db.Column(db.Integer, db.ForeignKey('appel_offre.id'), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseur.id'), nullable=False)
    montant_offre = db.Column(db.Numeric(15,2), nullable=False)
    proposition = db.Column(db.Text, nullable=False)
    statut = db.Column(db.Enum('En Attente', 'Acceptée', 'Rejetée'), default='En Attente')
    date_soumission = db.Column(db.DateTime, default=db.func.current_timestamp())

    appel_offre = db.relationship('AppelOffre', backref='offres')
    fournisseur = db.relationship('Fournisseur', backref='offres')

class ContratApprouve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appel_offre_id = db.Column(db.Integer, db.ForeignKey('appel_offre.id'), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseur.id'), nullable=False)
    valeur_contrat = db.Column(db.Numeric(15,2), nullable=False)
    date_attribution = db.Column(db.DateTime, default=db.func.current_timestamp())

    appel_offre = db.relationship('AppelOffre', backref='contrats_approuves')
    fournisseur = db.relationship('Fournisseur', backref='contrats_approuves')

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appel_offre_id = db.Column(db.Integer, db.ForeignKey('appel_offre.id'))
    offre_id = db.Column(db.Integer, db.ForeignKey('offre.id'))
    nom_fichier = db.Column(db.String(255), nullable=False)
    type_fichier = db.Column(db.String(50))
    lien_fichier = db.Column(db.Text, nullable=False)
    date_telechargement = db.Column(db.DateTime, default=db.func.current_timestamp())

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'user' or 'fournisseur'
    action = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def user(self):
        if self.user_type == 'user':
            return User.query.get(self.user_id)
        elif self.user_type == 'fournisseur':
            return Fournisseur.query.get(self.user_id)
        return None