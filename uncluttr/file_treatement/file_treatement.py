""" This module contains functions to treat files. """

import configparser
import zipfile
import os
import sys
import fitz
from uncluttr.core.configuration import get_base_app_files_path
import re
import nltk
import spacy
from nltk.corpus import stopwords
from spacy.lang.fr import French
import joblib  # Pour sauvegarder et charger le modèle ML
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC  # Exemple de modèle ML
import unicodedata


# Télécharger les stopwords de NLTK
nltk.download('stopwords')

# Charger le modèle spaCy pour le français
nlp = spacy.load("fr_core_news_sm")

# Supprimer les accents pour une optionnalité
def enlever_accents(texte):
    return ''.join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')

# Prétraitement du texte
def preprocess_text(texte):
    # Texte en minuscules
    texte = texte.lower()

    # Suppression des caractères non alphabétiques et des espaces supplémentaires
    texte = re.sub(r'[^a-zA-Zéàèùâêîôûçäëïöüôâàèéùê]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()

    # Suppression des accents (si nécessaire)
    texte = enlever_accents(texte)

    # Tokenisation et lemmatisation avec spaCy
    doc = nlp(texte)
    texte_lematise = " ".join([token.lemma_ for token in doc if token.lemma_ not in stopwords.words('french')])

    return texte_lematise.strip()


def is_structured_pdf(file_path: str) -> bool:
    """Check if the file is a structured PDF.

    :param str file_path: The path to the file.
    :return bool: _description_
    """
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                return True
    return False


def folder_analysis(path:str=None):
    """Analyzing files in a folder.

    :param str path: path to the folder to analyse, defaults to None
    """
    try:
        if path is None:
            config = configparser.ConfigParser()
            base_path = get_base_app_files_path()
            config_path = os.path.join(base_path, 'configuration', 'conf.ini')
            config.read(config_path)
            path = config['settings']['directory_to_watch']

        print(f"Analyzing files in {path}...")
        sys.stdout.flush()
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    file_analysis(os.path.join(root, file))
                except PermissionError as e:
                    print(f"Permission error: {e}")
                except FileNotFoundError as e:
                    print(f"File not found: {e}")
                except Exception as e:
                    print(f"An error occurred during file analysis: {e}")
    except NotADirectoryError as e:
        print(f"{path} is not a directory.")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An error occurred during folder analysis: {e}")

# Extraire le texte d'un PDF structuré
def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as doc:
        texte = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texte += page.get_text("text")
    return texte

# Extraire les mots-clés d'un texte
def extraire_mots_cles(texte):
    vectorizer = TfidfVectorizer(max_features=10)
    tfidf_matrix = vectorizer.fit_transform([texte])
    mots_cles = vectorizer.get_feature_names_out()

    return mots_cles

# Classifier le type de document
def classifier_document(texte):
    model_path = "model_svm.joblib"
    vectorizer_path = "vectorizer_tfidf.joblib"

    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    else:
        print("Modele de classification ou vectoriseur introuvable. Veuillez entrainer le modele d'abord.\n")
        return "Inconnu"

    texte_nettoye = preprocess_text(texte)
    vecteur = vectorizer.transform([texte_nettoye])
    prediction = classifier.predict(vecteur)
    return prediction[0]

def file_analysis(file_path: str = None):
    """Analyse a file.

    :param str file_path: path to the file to analyse, defaults to None
    """
    try:
        root, file = os.path.split(file_path)
        file_type = os.path.splitext(file_path)[1]
        match file_type:
            case '.zip':
                extract_path = os.path.join(root, os.path.splitext(file)[0])
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                os.remove(file_path)

                print(file_path, "extracted.")
                sys.stdout.flush()
                folder_analysis(extract_path)

            case '.pdf':
                print(f"Analyzing {file_path} ...")
                if is_structured_pdf(file_path):
                    # puis on envoie la team IA commme il se doit

                    print(f"\n\n{file_path.encode('utf-8', errors='replace').decode('utf-8')} is a structured PDF.\n")
                    texte_pdf = extract_text_from_pdf(file_path)

                    texte_nettoye = preprocess_text(texte_pdf)
                    print(f"Nettoyage du texte termine.\n")

                    mots_cles = extraire_mots_cles(texte_nettoye)
                    print(f"Mots-cles du PDF: {mots_cles}\n")

                    type_document = classifier_document(texte_pdf)
                    print(f"Type de document : {type_document}\n")
                    sys.stdout.flush()

                else:
                    print(f"{file_path} is an unstructured PDF.\n")
                    # puis on envoie la team IA commme il se doit
                sys.stdout.flush()
            case _:
                print(f"{file_path} is not a file type we currently handle.")
                sys.stdout.flush()
    except zipfile.BadZipFile as e:
        print(f"Bad zip file: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during file analysis: {e}")

# Exemple pour entraîner le modèle
def entrainer_modele():
    textes = [
    # Factures
    "Facture numéro 1234, client : John Doe, total : 500 euros, frais de service : 800 euros ht, ",
    "Facture pour services rendus, montant total : 300 euros, TVA incluse, ht, montant, frais",
    "FACTURE N° 31199, N° de Facture : 31199, Commande : , Tel. : , Email : , Fax : TVA Quantité Prix de vente Unitaire, Frais HT Unitaire, Montant prix de base HT, prix de base TTC, MONTANT TTC EN EUROS 337,00, Règlement, CARTE BANCAIRE, 338,45 €, Taux TVA HT TTC",
    
    #Devis
    "DEVIS N°12345, DESCRIPTION PRIX QUANTITÉ TOTAL, 40€, Date du devis : 10/12/22, Validité du devis : 1 mois, Sous total : 160 €, TVA (20%) : 32 €, TOTAL : 182 €",
    "compte client, INFORMATIONS DE PAIEMENT : Par virement bancaire, 30% d'acompte à verser à la signature du contrat, Signature du client",
    "DEVIS N°12345, estimation pour travaux de plomberie, validité : 15 jours, total : 300 euros, TVA incluse.",
    "Offre de prix pour services de réparation, sous-total : 400 euros, validité jusqu'au 01/02/2023, signature pour acceptation.",
    "Estimation des coûts pour le projet informatique, validité 1 mois, total TTC : 2500 euros.DEVIS, TOTAL, Sous total, TVA, Signature, Acompte",

    #Contrats
    "Contrat de travail à durée déterminée : engagement de 6 mois, clause de confidentialité incluse.",
    "Contrat de sous-traitance : le prestataire s'engage à fournir les services mentionnés dans les termes.",
    "Contrat de location : le locataire accepte les conditions spécifiées pour une période de 12 mois.",
    "Les termes de ce contrat de partenariat sont définis pour une collaboration jusqu'en 2025.",

    # Bons de commande
    "Bon de commande numéro 5678, fournisseur : ABC Corp, articles : 10",
    "Commande passée le 12 janvier, produits : fournitures de bureau, quantité : 50",
    
    # Fiches de paie
    "Fiche de paie du mois de janvier, employé : Jane Doe, salaire : 3000 euros ht, montant, poste, horaire",
    "Bulletin de salaire : période d'emploi du 1er au 31 mars, net à payer : 2500 euros, date de paiement",
    "Date de paiement, Matricule, N° SIRET: N° APE:, Impôt sur le revenu Base Montant, DATE DESIGNATION BASE, PART EMPLOYE, TAUX MONTANT, EMPLOYEUR, MONTANT, TRAVAIL INCIDENT, NET A PAYER, AFFECTATION : , POSTE : , EMPLOI NCC :, HORAIRE MENSUEL 156,00, DEBUT CONTRAT : , D. ANCIENNETE : , 01 2024, BRUT SS 3076,10 10167,22, BRUT IMPOSABLE, NET FISCAL 2805,36 9839,36, COTISations SALARIALES, COTIS. PATRONALES, TOTAL VERSE EMPLOYEUR, HS/HC EXO FISCALES, Droit Pris Solde, CONGES PAYES, NET À PAYER AVANT IMPÔT SUR LE REVENU, MONTANT NET SOCIAL, VIREMENT, EXONÉRATION DE COTISATIONS SALARIALE, Impôt sur le revenu prélevé à la source, AUTRES RETENUES, DONNEES FISCALES, Traitements et salaires, HS/HC exonérées",

    # Articles de presse
    "Article de presse : le réchauffement climatique menace les écosystèmes marins",
    "Dans un article publié récemment, les chercheurs alertent sur la fonte des glaciers",
    "Le dernier rapport sur l'économie mondiale met en lumière les inégalités sociales",
    
    # Recherches sur un sujet
    "Recherche scientifique sur l'intelligence artificielle et ses applications",
    "Étude publiée dans une revue académique sur les effets des pesticides, expérience, pourcentage, analyse, connaissance, source des informations",
    "Document de recherche : analyse de la relation entre la nutrition et la santé mentale",

    #Procédure/méthode/guide d'utilisation
    "Guide d'utilisation : comment configurer votre logiciel en quelques étapes simples.",
    "Procédure pour la gestion des incidents techniques dans l'entreprise.",
    "Ce document décrit la méthode de calcul des coûts pour les projets de développement.",
    "Guide utilisateur : manuel détaillé pour l'installation et l'utilisation du produit.",
    "Procédure d'audit interne : identification des processus clés, évaluation des contrôles internes, recommandations d'améliorations.",
    "Procédure de gestion des ressources humaines : recrutement, formation, évaluation des performances.",

    #Référentiels
    "Référentiel de compétences professionnelles pour les employés de l'entreprise.",
    "Référentiel interne : normes et pratiques pour la gestion des projets informatiques.",
    "Guide de conformité basé sur le référentiel RGPD pour la protection des données personnelles.",
    "Référentiel technique pour les équipements industriels utilisés dans nos usines.",
    "Référentiel ISO 9001 : 2015, normes pour le management de la qualité, exigences pour la gestion des processus.",
    "Référentiel RGPD : gestion des données personnelles, exigences légales pour la protection des données.",
    "Référentiel des bonnes pratiques en cybersécurité : prévention des menaces, gestion des vulnérabilités, planification de la reprise après sinistre."

    ]

    labels = [
    "facture", 
    "facture",
    "facture",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "bon_de_commande", 
    "bon_de_commande",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "recherche", 
    "recherche", 
    "recherche",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel"
    ]

    textes_pretraites = [preprocess_text(t) for t in textes]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textes_pretraites)
    classifier = SVC()
    classifier.fit(X, labels)

    joblib.dump(classifier, "model_svm.joblib")
    joblib.dump(vectorizer, "vectorizer_tfidf.joblib")
    print("\nentrainement effectue.\n")
