from flask_login import UserMixin
from datetime import datetime
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class Fournisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    entreprise = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    date_inscription = db.Column(db.DateTime, default=db.func.current_timestamp())

class AppelOffre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date_lancement = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_limite = db.Column(db.DateTime, nullable=False)
    budget_estime = db.Column(db.Numeric(15,2), nullable=False)
    statut = db.Column(db.Enum('ouvert', 'fermé', 'attribué'), default='ouvert')
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='appels_offres')

class Offre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appel_offre_id = db.Column(db.Integer, db.ForeignKey('appel_offre.id'), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseur.id'), nullable=False)
    montant_offre = db.Column(db.Numeric(15,2), nullable=False)
    proposition = db.Column(db.Text, nullable=False)
    statut = db.Column(db.Enum('en_attente', 'acceptée', 'rejetée'), default='en_attente')
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='history')