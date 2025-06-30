from flask import Flask, abort, flash, redirect, render_template, request, url_for,session
from flask_sqlalchemy import SQLAlchemy
from models import ContratApprouve, History, Offre, db,AppelOffre,Fournisseur,Document, User, bcrypt
from flask_migrate import Migrate
from forms import ContactForm, EditUserForm, FrssForm,EditFrssForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object('config.Config')
# Initialisation de la base de données avec SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

bcrypt.init_app(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
# Ajouter une variable pour stocker le répertoire de téléchargement
UPLOAD_FOLDER = 'static/uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER_DOC = 'static/uploads/upload_documents'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg'}
app.config['UPLOAD_FOLDER_DOC'] = UPLOAD_FOLDER_DOC

UPLOAD_FOLDER_PROGRAMMES = 'static/uploads/upload_progs'
app.config['UPLOAD_FOLDER_PROGRAMMES'] = UPLOAD_FOLDER_PROGRAMMES

UPLOAD_FOLDER_SOC = 'static/uploads/upload_social'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg'}
app.config['UPLOAD_FOLDER_SOC'] = UPLOAD_FOLDER_SOC
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Fonction pour vérifier les types de fichiers autorisés
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'user':
        return User.query.get(int(user_id))
    elif user_type == 'fournisseur':
        return Fournisseur.query.get(int(user_id))
    return None

def log_history(action):
    if current_user.is_authenticated:  # Vérifie si l'utilisateur est connecté
        new_entry = History(user_id=current_user.id, action=action)
        db.session.add(new_entry)
        db.session.commit()


# Page d'accueil
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/avisdoffre')
def avisdoffre():
    appels_offres = AppelOffre.query.all()
    return render_template('avisdoffre.html', appels_offres=appels_offres)

@app.route('/ajouter_appel_offre', methods=['GET', 'POST'])
@login_required
def ajouter_appel_offre():
    # Vérifier que l'utilisateur est admin
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('avisdoffre'))
    
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        date_limite = datetime.strptime(request.form['date_limite'], '%Y-%m-%d').date()
        budget_estime = float(request.form['budget_estime'])
        
        # Vérifier que la date limite n'est pas dans le passé
        if date_limite <= datetime.now().date():
            flash('La date limite doit être dans le futur', 'error')
            return render_template('ajouter_appel_offre.html', 
                                 titre=titre, 
                                 description=description, 
                                 budget_estime=budget_estime)
        
        # Créer un nouvel appel d'offre
        nouvel_appel = AppelOffre(
            titre=titre,
            description=description,
            date_lancement=datetime.now().date(),
            date_limite=date_limite,
            budget_estime=budget_estime,
            statut='ouvert',
            cree_par=current_user.id
        )
        
        try:
            db.session.add(nouvel_appel)
            db.session.commit()
            
            flash('Appel d\'offre créé avec succès', 'success')
            # Utiliser le user_type de la session ou déterminer automatiquement
            user_type = session.get('user_type', 'user')  # 'user' par défaut pour les admins
            log_history(f"L'administrateur {current_user.name} a créé un nouvel appel d'offre: {titre}", user_type)
            return redirect(url_for('avisdoffre'))
        
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création de l\'appel d\'offre', 'error')
            return render_template('ajouter_appel_offre.html')
    
    return render_template('ajouter_appel_offre.html')

@app.route('/avisdoffre/<int:id>')
def detail_ao(id):
    appel_offre = AppelOffre.query.get_or_404(id)
    return render_template('detail_ao.html', appel_offre=appel_offre)

@app.route('/avisdoffre/<int:id>/ajouter_offre', methods=['GET', 'POST'])
@login_required
def ajouter_offre(id):
    appel_offre = AppelOffre.query.get_or_404(id)
    fournisseurs = Fournisseur.query.all()

    if request.method == 'POST':
        fournisseur_id = request.form['fournisseur'] 
        montant_offre = request.form['montant_offre']
        proposition = request.form['proposition']
        
        # Créer une nouvelle offre
        nouvelle_offre = Offre(
            fournisseur_id=fournisseur_id,
            montant_offre=montant_offre,
            proposition=proposition,
            appel_offre_id=id
        )
        
        db.session.add(nouvelle_offre)
        db.session.commit()
        
        flash('Offre ajoutée avec succès', 'success')
        log_history(f"L'utilisateur {current_user.name} a soumis une offre pour l'appel d'offre {id}")
        return redirect(url_for('detail_ao', id=id))
    
    return render_template('ajouter_offre.html', appel_offre=appel_offre, fournisseurs=fournisseurs)

@app.route('/avisdoffre/<int:id>/supprimer_offre/<int:offre_id>', methods=['GET', 'POST'])
@login_required
def supprimer_offre(id, offre_id):
    appel_offre = AppelOffre.query.get_or_404(id)
    offre = Offre.query.get_or_404(offre_id)
    
    try:
        db.session.delete(offre)  # Supprimer l'offre
        db.session.commit()  # Sauvegarder la suppression
        flash('Offre supprimée avec succès.', 'success')
        log_history(f"L'utilisateur {current_user.name} a supprimé l’offre {offre_id} de l'appel d'offre {id}")
    except:
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression de l\'offre.', 'error')

    return redirect(url_for('detail_ao', id=id))  # Rediriger vers la page de détails de l'appel d'offre

@app.route('/attribuer_marche/<int:appel_offre_id>/<int:offre_id>', methods=['GET', 'POST'])
@login_required
def attribuer_marche(appel_offre_id, offre_id):
    # Vérifier si l'utilisateur est admin
    if current_user.role != 'admin':
        flash("Vous n'avez pas l'autorisation de réaliser cette action.", 'danger')
        return redirect(url_for('home'))

    # Récupérer l'appel d'offre et l'offre
    appel_offre = AppelOffre.query.get_or_404(appel_offre_id)
    offre = Offre.query.get_or_404(offre_id)

    # Vérifier si l'appel d'offre est ouvert et si l'offre n'est pas déjà acceptée
    if appel_offre.statut != 'Ouvert':
        flash("Cet appel d'offre n'est pas dans un état valide pour l'attribution.", 'danger')
        return redirect(url_for('detail_ao', id=appel_offre_id))

    if request.method == 'POST':
        files = request.files.getlist('documents')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Créer un document associé à l'offre
                document = Document(
                    appel_offre_id=appel_offre.id,
                    offre_id=offre.id,
                    nom_fichier=filename,
                    type_fichier=file.content_type,
                    lien_fichier=file_path
                )
                db.session.add(document)
            else:
                flash("Le type de fichier n'est pas autorisé. Veuillez télécharger un fichier avec les extensions suivantes : pdf, doc, docx, jpg, png, jpeg.", 'danger')
                return redirect(url_for('attribuer_marche', appel_offre_id=appel_offre_id, offre_id=offre_id))

        appel_offre.statut = 'Attribué'
        offre.statut = 'Acceptée'
        contrat = ContratApprouve(
            appel_offre_id=appel_offre.id,
            fournisseur_id=offre.fournisseur_id,
            valeur_contrat=offre.montant_offre
        )
        db.session.add(contrat)
        db.session.commit()

        flash(f"Le marché a été attribué à {offre.fournisseur.nom} avec succès.", 'success')
        return redirect(url_for('marchesattribues'))
    return render_template('attribuer_marche.html', appel_offre=appel_offre, offre=offre)

@app.route('/rejeter_offre/<int:appel_offre_id>/<int:offre_id>')
@login_required
def rejeter_offre(appel_offre_id, offre_id):
    # Récupérer l'offre depuis la base de données
    offre = Offre.query.get_or_404(offre_id)
    appel_offre = AppelOffre.query.get_or_404(appel_offre_id)

    # Vérifier si l'offre a déjà un statut attribué
    if appel_offre.statut != 'Ouvert':
        flash("Cet appel d'offre n'est pas dans un état valide pour la rejection.", 'danger')
        return redirect(url_for('detail_ao', id=appel_offre_id))

    if offre.statut == "Rejetée":
        flash("Cette offre a déjà été rejetée.", "warning")
        return redirect(url_for('detail_ao', id=appel_offre_id))

    # Mettre à jour le statut de l'offre
    offre.statut = "Rejetée"
    db.session.commit()

    flash("L'offre a été rejetée avec succès.", "success")
    return redirect(url_for('detail_ao', id=appel_offre_id))

@app.route('/marchesattribues')
def marchesattribues():
    contrats = ContratApprouve.query.join(AppelOffre).join(Fournisseur).all()
    return render_template('marchesattribues.html', contrats=contrats)
    # return render_template('marchesattribues.html')

@app.route('/marchesattribues/<int:id>')
def marchesattribues_details(id):
    contrat = ContratApprouve.query.get_or_404(id)  # Récupère le contrat attribué par son ID
    documents = Document.query.filter((Document.appel_offre_id == contrat.appel_offre_id) | (Document.offre_id == contrat.id)).all()
    return render_template('marchesattribues_details.html', contrat=contrat, documents=documents)


# @app.route('/demaprogsoc')
# def demaprogsoc():
#     return render_template('demaprogsoc.html')

@app.route('/demaprogsoc')
def demaprogsoc():
    """Affiche la page de démarche progrès social avec gestion des documents"""
    folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_SOC'])
    documents = []
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for filename in os.listdir(folder):
        if allowed_file(filename):
            filepath = os.path.join(folder, filename)
            stat = os.stat(filepath)
            name_upper = filename.upper()  # Utiliser uppercase pour comparer les suffixes

            # Détection stricte de la langue
            if ' VF ' in name_upper or name_upper.endswith('VF') or name_upper.endswith('VF.PDF'):
                language = 'fr'
            elif ' VA ' in name_upper or name_upper.endswith('VA') or name_upper.endswith('VA.PDF'):
                language = 'ar'
            elif ' fr ' in name_upper or name_upper.endswith('fr') or name_upper.endswith('FR.PDF'):
                language = 'fr'
            elif ' AR' in name_upper or name_upper.endswith('AR') or name_upper.endswith('AR.PDF'):
                language = 'ar'
            else:
                language = 'autre'

            # Nom lisible
            display_name = filename
            if 'CHARTE' in name_upper:
                if language == 'ar':
                    display_name = "Charte Achats Responsables - Version Arabe"
                elif language == 'fr':
                    display_name = "Charte Achats Responsables - Version Française"
                else:
                    display_name = "Charte Achats Responsables - Autre Version"

            documents.append({
                'name': filename,
                'display_name': display_name,
                'language': language,
                'size': round(stat.st_size / 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y')
            })
    
    return render_template('demaprogsoc.html', documents=documents)


@app.route('/upload_document_soc', methods=['POST'])
def upload_document_soc():
    """Upload un nouveau document"""
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('demaprogsoc'))
    
    file = request.files['file']
    display_name = request.form.get('display_name', '')
    language = request.form.get('language', 'fr')
    
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('demaprogsoc'))
    
    if file and allowed_file(file.filename):
        # Créer un nom de fichier basé sur le nom d'affichage et la langue
        original_ext = os.path.splitext(file.filename)[1]
        if display_name:
            # Nettoyer le nom d'affichage pour en faire un nom de fichier valide
            clean_name = "".join(c for c in display_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{clean_name}_{language}{original_ext}"
        else:
            filename = file.filename
        
        filename = secure_filename(filename)
        upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_SOC'])
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        
        file.save(os.path.join(upload_path, filename))
        flash('Document téléversé avec succès!', 'success')
    else:
        flash('Type de fichier non autorisé', 'error')
    
    return redirect(url_for('demaprogsoc'))

@app.route('/delete_document_soc/<filename>', methods=['POST'])
def delete_document_soc(filename):
    """Supprime un document"""
    try:
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_SOC'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('Document supprimé avec succès!', 'success')
        else:
            flash('Fichier non trouvé', 'error')
    except Exception as e:
        flash('Erreur lors de la suppression du fichier', 'error')
    
    return redirect(url_for('demaprogsoc'))

@app.route('/rename_document_soc/<filename>', methods=['POST'])
def rename_document_soc(filename):
    """Renomme un document"""
    new_display_name = request.form.get('new_display_name')
    new_language = request.form.get('new_language', 'fr')
    
    if not new_display_name:
        flash('Nouveau nom requis', 'error')
        return redirect(url_for('demaprogsoc'))
    
    try:
        # Conserver l'extension originale
        original_ext = os.path.splitext(filename)[1]
        
        # Créer le nouveau nom de fichier
        clean_name = "".join(c for c in new_display_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        new_filename = f"{clean_name}_{new_language}{original_ext}"
        new_filename = secure_filename(new_filename)
        
        old_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_SOC'], filename)
        new_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_SOC'], new_filename)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            flash('Document renommé avec succès!', 'success')
        else:
            flash('Fichier non trouvé', 'error')
    except Exception as e:
        flash('Erreur lors du renommage du fichier', 'error')
    
    return redirect(url_for('demaprogsoc'))

@app.route('/reglmarch')
def reglmarch():
    return render_template('reglmarch.html')
from datetime import datetime

@app.route('/reglmarch/documents')
# def documents():
#     return render_template('documents.html')
def documents():
    folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_DOC'])
    files = []
    for filename in os.listdir(folder):
        if allowed_file(filename):
            filepath = os.path.join(folder, filename)
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': round(stat.st_size / 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y')
            })
    return render_template('documents.html', files=files)
@app.route('/reglmarch/documents/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER_DOC'], filename)
        file.save(save_path)
        flash('Document ajouté avec succès.')
    else:
        flash('Fichier non autorisé.')
    return redirect(url_for('documents'))
@app.route('/reglmarch/documents/delete/<filename>', methods=['POST'])
def delete_document(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER_DOC'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Document supprimé.')
    else:
        flash('Fichier introuvable.')
    return redirect(url_for('documents'))

@app.route('/reglmarch/documents/rename/<filename>', methods=['POST'])
def rename_document(filename):
    new_name_input = secure_filename(request.form['new_name'])
    old_path = os.path.join(app.config['UPLOAD_FOLDER_DOC'], filename)

    # Extraire l'extension existante
    extension = os.path.splitext(filename)[1]  # ex: ".pdf"

    # S'assurer que la nouvelle extension est identique
    if not new_name_input.lower().endswith(extension.lower()):
        new_name = new_name_input + extension
    else:
        new_name = new_name_input

    new_path = os.path.join(app.config['UPLOAD_FOLDER_DOC'], new_name)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        flash('Fichier renommé avec succès.')
    else:
        flash('Fichier introuvable.')

    return redirect(url_for('documents'))

# @app.route('/proginvest')
# def proginvest():
#     return render_template('proginvest.html')
@app.route('/proginvest')
def proginvest():
    """Affiche la page des programmes d'investissement avec gestion des fichiers"""
    folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PROGRAMMES'])
    programmes = []
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for filename in os.listdir(folder):
        if allowed_file(filename):
            filepath = os.path.join(folder, filename)
            stat = os.stat(filepath)
            
            # Déterminer le nom d'affichage basé sur le nom du fichier
            display_name = filename
            if 'tanger' in filename.lower():
                display_name = "Programme Prévisionnel Tanger"
            elif 'tetouan' in filename.lower() or 'tétouan' in filename.lower():
                display_name = "Programme Prévisionnel Tétouan"
            
            programmes.append({
                'name': filename,
                'display_name': display_name,
                'size': round(stat.st_size / 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y')
            })
    
    return render_template('proginvest.html', programmes=programmes)

@app.route('/upload_programme', methods=['POST'])
def upload_programme():
    """Upload un nouveau programme d'investissement"""
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PROGRAMMES'])
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        
        file.save(os.path.join(upload_path, filename))
        flash('Programme d\'investissement téléversé avec succès!', 'success')
    else:
        flash('Type de fichier non autorisé', 'error')
    
    return redirect(url_for('proginvest'))

@app.route('/delete_programme/<filename>', methods=['POST'])
def delete_programme(filename):
    """Supprime un programme d'investissement"""
    try:
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PROGRAMMES'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('Programme d\'investissement supprimé avec succès!', 'success')
        else:
            flash('Fichier non trouvé', 'error')
    except Exception as e:
        flash('Erreur lors de la suppression du fichier', 'error')
    
    return redirect(url_for('proginvest'))

@app.route('/rename_programme/<filename>', methods=['POST'])
def rename_programme(filename):
    """Renomme un programme d'investissement"""
    new_name = request.form.get('new_name')
    if not new_name:
        flash('Nouveau nom requis', 'error')
        return redirect(url_for('proginvest'))
    
    try:
        # Ajouter l'extension si elle n'est pas présente
        if not any(new_name.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx']):
            # Conserver l'extension originale
            original_ext = os.path.splitext(filename)[1]
            new_name += original_ext
        
        old_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PROGRAMMES'], filename)
        new_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PROGRAMMES'], secure_filename(new_name))
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            flash('Programme d\'investissement renommé avec succès!', 'success')
        else:
            flash('Fichier non trouvé', 'error')
    except Exception as e:
        flash('Erreur lors du renommage du fichier', 'error')
    
    return redirect(url_for('proginvest'))
from flask_mail import Mail, Message

# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'alikhl66644@gmail.com'
app.config['MAIL_PASSWORD'] = 'aytg hjyb lthp bych'
app.config['MAIL_DEFAULT_SENDER'] = 'alikhl66644@gmail.com'

mail = Mail(app)


@app.route('/contacternous', methods=["GET", "POST"])
def contacternous():
    form = ContactForm()
    if form.validate_on_submit():
        type_demande = form.type_demande.data
        email = form.email.data
        observations = form.observations.data

        if type_demande == "rec_anon":
            societe = "N/A"
            secteur = "N/A"
            nom_prenom = "Anonyme"
            telephone = "N/A"
        else:
            societe = form.societe.data
            secteur = form.secteur.data
            nom_prenom = form.nom_prenom.data
            telephone = form.telephone.data

        # Envoi d'un email
        admin_email = "alikhl66644@gmail.com"
        msg = Message("Demande de contact - Nouvelle soumission", sender="alikhl66644@gmail.com", recipients=[admin_email])
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; padding: 20px;">
                <div style="text-align: center; background-color: #d9d9d9; color: #FA0504; padding: 10px; display: flex; align-items: center; justify-content: space-between;">
    <img src="https://www.matfoot.com/wp-content/uploads/2018/10/logo2.png" alt="Logo" style="width:60px;" />
    <h1 style="flex-grow: 1; text-align: center;">Demande de Contact</h1>
</div>

                <div style="text-align: center; background-color: #FA0504; color: white; padding: 2px;">
                </div>
                <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                    <p>Bonjour Ikram,</p>
                    <p>Nous vous informons qu'une nouvelle demande de contact a été soumise via le site web. Voici les détails de la demande :</p>
                    <p><span style="color:#B23A3B;"><strong>Objet de la demande :</strong></span> {type_demande}</p>
                    <p><span style="color:#B23A3B;"><strong>Société :</strong></span> {societe}</p>
                    <p><span style="color:#B23A3B;"><strong>Secteur d'activité :</strong></span> {secteur}</p>
                    <p><span style="color:#B23A3B;"><strong>Nom et Prénom :</strong></span> {nom_prenom}</p>
                    <p><span style="color:#B23A3B;"><strong>Téléphone :</strong></span> {telephone}</p>
                    <p><span style="color:#B23A3B;"><strong>E-mail :</strong></span> {email}</p>
                    <p><span style="color:#B23A3B;"><strong>Observations supplémentaires :</strong></span> {observations}</p>
                </div>
                <div style="background-color: #FA0504; padding: 2px;">
                </div>

                <div style="text-align: center; font-size: 14px; color: black;">
                    <p>Merci de bien vouloir vérifier et prendre les mesures nécessaires pour répondre à cette demande dans les plus brefs délais.</p>
                    <img src="https://www.matfoot.com/wp-content/uploads/2018/10/logo2.png" alt="Logo"   />
                </div>

            </body>
        </html>
        """
        msg.content_type = 'text/html'
        try:
            mail.send(msg)
            flash("Votre message a été envoyé avec succès!", "success")
        except Exception as e:
            flash(f"Erreur lors de l'envoi de l'email: {str(e)}", "danger")

        return redirect(url_for("contacternous"))

    return render_template('contacternous.html', form=form)

@app.route('/inscription_frss', methods=['GET', 'POST'])
@login_required
def inscription_frss():
    if session.get('user_type') != 'user' or current_user.role != 'admin':
        abort(403)
    form = FrssForm()
    print("🔍 Method:", request.method)
    print("✅ Form submitted:", form.is_submitted())
    print("✅ Form valid:", form.validate_on_submit())
    print("📝 Form errors:", form.errors)

    if request.method == 'POST':
        # Force confirm_password to match password
        form.confirm_password.data = form.password.data
    if form.validate_on_submit():
        entreprise = form.entreprise.data if form.entreprise.data else form.nom.data

        new_frss = Fournisseur(
            nom=form.nom.data,
            email=form.email.data,
            entreprise=entreprise,
            telephone=form.telephone.data,
            adresse=form.adresse.data
        )
        
        new_frss.set_password(form.password.data)

        # Ajout du fournisseur à la base de données
        db.session.add(new_frss)
        db.session.commit()

        # Flash message pour confirmer l'inscription
        flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('login')) 
    return render_template('inscription_frss.html',form=form)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        fournisseur = Fournisseur.query.filter_by(email=form.email.data).first()
        if user:  # Vérifier si c'est un utilisateur normal
            if user.check_password(form.password.data):
                login_user(user)
                session['user_type'] = 'user'
                flash("Connexion réussie en tant qu'utilisateur.", "success")
                return redirect(url_for('home'))
            else:
                flash("Mot de passe incorrect.", "danger")
                return redirect(url_for('login'))

        elif fournisseur:  # Vérifier si c'est un fournisseur
            if fournisseur.check_password(form.password.data):
                login_user(fournisseur)
                session['user_type'] = 'fournisseur'
                flash("Connexion réussie en tant que fournisseur.", "success")
                return redirect(url_for('home'))
            else:
                flash("Mot de passe incorrect.", "danger")
                return redirect(url_for('login'))

        else:
            flash("Aucun compte trouvé avec cet email.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)
    # return render_template('login.html', transparent_navbar=False)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('home'))

@app.route('/historique')
@login_required
def historique():
    if session.get('user_type') != 'user' or current_user.role != 'admin':
        abort(403)
    history = History.query.order_by(History.timestamp.desc()).all()
    return render_template('historique.html', history=history)

@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html'), 403

@app.errorhandler(403)
def access_forbidden(error):
    return render_template("unauthorized.html"), 403

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    is_fournisseur = hasattr(current_user, 'entreprise')
    print("🔍 Type d'utilisateur:", "Fournisseur" if is_fournisseur else "Admin/User")

    # Choix du bon formulaire
    if is_fournisseur:
        form = EditFrssForm(obj=current_user)
    else:
        form = EditUserForm(obj=current_user)

    if form.validate_on_submit():
        print("✅ Formulaire validé")

        if is_fournisseur:
            current_user.nom = form.nom.data
            current_user.email = form.email.data
            current_user.entreprise = form.entreprise.data
            current_user.telephone = form.telephone.data
            current_user.adresse = form.adresse.data
        else:
            current_user.name = form.name.data
            current_user.email = form.email.data

        # Si la case "Modifier le mot de passe" est cochée, on met à jour le mot de passe
        if 'change_password' in request.form:
            print("🔐 Nouveau mot de passe :", form.password.data)
            if form.password.data:  # Si un mot de passe est fourni
                current_user.set_password(form.password.data)
                print("✅ Mot de passe mis à jour avec set_password()")
                db.session.add(History(user_id=current_user.id, action="Changement de mot de passe"))
                flash("Mot de passe mis à jour.", "info")
            else:
                print("⚠️ Aucun mot de passe fourni")
                flash("⚠️ Vous avez coché la case de changement du mot de passe mais n'avez pas saisi de mot de passe.", "danger")
                return render_template('edit_profile.html', form=form, is_fournisseur=is_fournisseur)

        # Log de modification
                # 🔍 Détecter si c’est un Fournisseur ou un User
        if hasattr(current_user, 'nom'):  # Fournisseur
            user_type = 'fournisseur'
            user_id = current_user.id
            utilisateur_nom = current_user.nom
        else:
            user_type = 'user'
            user_id = current_user.id
            utilisateur_nom = current_user.name

        # 🔧 Affichage debug
        print("🔍 Type d'utilisateur:", user_type.capitalize())
        print("👤 Nom connecté :", utilisateur_nom)
        print("📧 Email connecté :", current_user.email)
        print("🆔 ID connecté :", user_id)

        # 🔁 Récupérer le nom modifié dans le formulaire
        form_nom = form.nom.data if is_fournisseur else form.name.data

        # 📝 Définir l'action
        if utilisateur_nom == form_nom:
            action_texte = f"{utilisateur_nom} a modifié son propre profil"
        else:
            action_texte = f"{utilisateur_nom} a modifié le profil de {form_nom}"

        # ✅ Log de l'action à la console
        print(f"📝 Historique enregistré → User ID: {user_id} | Type: {user_type} | Action: {action_texte}")

        # 📥 Enregistrement dans la base
        db.session.add(History(
            user_id=user_id,
            user_type=user_type,
            action=action_texte
        ))
        db.session.commit()
        flash('Votre profil a été mis à jour avec succès.', 'success')
        print("🆕 Nom saisi :", form_nom)
        print("📎 Nom actuel :", utilisateur_nom)  
        return redirect(url_for('profile'))
    else:
        if request.method == 'POST':
            print("❌ Formulaire non validé")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Erreur dans le champ {field}: {error}")

    return render_template('edit_profile.html', form=form, is_fournisseur=is_fournisseur)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
