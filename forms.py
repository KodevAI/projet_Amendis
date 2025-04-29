from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField ,PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional,Length,EqualTo

class ContactForm(FlaskForm):
    type_demande = SelectField(
        "Type de demande", 
        choices=[("info", "Demande d'info"), ("rec", "Réclamation"), ("rec_anon", "Réclamation Anonyme")], 
        validators=[DataRequired()]
    )
    
    # Ces champs ne seront requis que si la demande n'est pas anonyme
    societe = StringField("Nom de la société", validators=[Optional()])
    secteur = StringField("Secteur d'activité", validators=[Optional()])
    nom_prenom = StringField("Nom/Prénom", validators=[Optional()])
    telephone = StringField("N° de Téléphone", validators=[Optional()])
    
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    observations = TextAreaField("Observations", validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Se connecter')

class FrssForm(FlaskForm):
    nom = StringField('Nom et prénom', validators=[DataRequired()])
    email = StringField('E-mail',validators=[DataRequired(),Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[EqualTo('password', message='Les mots de passe doivent correspondre.')])
    entreprise = StringField("Nom de l'entreprise", validators=[DataRequired()])
    telephone=StringField('N° de Téléphone')
    adresse=StringField('Adresse')
    submit = SubmitField("S'inscrire")

class EditFrssForm(FlaskForm):
    nom = StringField('Nom et prénom', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirmer le mot de passe',
        validators=[Optional(), EqualTo('password', message='Les mots de passe doivent correspondre.')]
    )
    entreprise = StringField("Nom de l'entreprise", validators=[DataRequired()])
    telephone = StringField('N° de Téléphone', validators=[Optional()])
    adresse = StringField('Adresse', validators=[Optional()])
    submit = SubmitField("Modifier")

class EditUserForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[EqualTo('password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField('Mettre à jour')