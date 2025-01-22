""" Training models for document classification. """

import os
import joblib
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.text_preprocessing import preprocess_text

def entrainer_modele():
    textes = [
    # Factures
    "Facture numéro, client, total : 500 euros, frais de service : 800 euros ht,",
    "Facture pour services rendus, montant total : 300 euros, TVA incluse, ht, montant, frais",
    "FACTURE N° 31199, N° de Facture : 31199, Commande : , Tel. : , Email : , Fax : TVA Quantité Prix de vente Unitaire, Frais HT Unitaire, Montant prix de base HT, prix de base TTC, MONTANT TTC EN EUROS 337,00, Règlement, CARTE BANCAIRE, 338,45 €, Taux TVA HT TTC",
    
    #Devis
    "DEVIS N°12345, PRIX QUANTITÉ TOTAL, 40€, Date du devis : 10/12/22, devis, Sous total : 160 €, TVA (20%) : 32 €",
    "compte client, PAIEMENT : Par virement bancaire, 30% d'acompte à verser, Estimation des coûts, validité 1 mois, TVA ttc, Acompte",
    "DEVIS N°12345, estimation pour travaux, validité, total : 300 euros, TVA incluse, Offre de prix pour services de réparation, sous-total : 400 euros,",

    #Contrats
   "Contrat, Contractant, Prestataire, Employeur, Salarié, Partie prenante, Signataire, Donneur d’ordre, sous-traitance",
   "Accord, Prestations, Services, Obligations, Terme, Période d’essai, Résiliation, Renouvellement, Délai",
   "Échéance, Rupture anticipée, Clause résolutoire, Clause pénale, Indemnité",

    # Bons de commande
    "Bon de commande numéro 5678, fournisseur : ABC Corp, articles : 10",
    "Commande passée le 12 janvier, produits : fournitures de bureau, quantité : 50",
    
    # Fiches de paie
    "Fiche de paie, employé : Jane Doe, salaire : 3000 euros ht, montant, poste, horaire",
    "Bulletin de salaire : période d'emploi du 1er au 31 mars, net à payer : 2500 euros, date de paiement",
    "Date de paiement, Matricule, N° SIRET: N° APE:, Impôt sur le revenu Base Montant, DATE DESIGNATION BASE, PART EMPLOYE, TAUX MONTANT, EMPLOYEUR, MONTANT, TRAVAIL INCIDENT, NET A PAYER, AFFECTATION : , POSTE : , EMPLOI NCC :, HORAIRE MENSUEL 156,00, DEBUT CONTRAT : , D. ANCIENNETE : , 01 2024, BRUT SS 3076,10 10167,22, BRUT IMPOSABLE, NET FISCAL 2805,36 9839,36, COTISations SALARIALES, COTIS. PATRONALES, TOTAL VERSE EMPLOYEUR, HS/HC EXO FISCALES, Droit Pris Solde, CONGES PAYES, NET À PAYER AVANT IMPÔT SUR LE REVENU, MONTANT NET SOCIAL, VIREMENT, EXONÉRATION DE COTISATIONS SALARIALE, Impôt sur le revenu prélevé à la source, AUTRES RETENUES, DONNEES FISCALES, Traitements et salaires, HS/HC exonérées",

   # Articles de presse
   "Article de presse, Critique, Point de vue, Editorial, Chronique, Source, Citation, Reporteur, Journaliste, Agence de presse, Titre, Accroche, , Sujet d’actualité, Contexte, Enjeu",
   "Dans un article publié récemment, Information, Témoignage, Enquête, Reportage, Déclaration, Annonce, Révélation, Débat, Controverse",
   "Faits divers, Politique, Société, Économie, Environnement, Technologie, Santé, Culture, Sport, International, interview",
   
   # Recherches sur un sujet
   "Recherche scientifique sur l'intelligence artificielle et ses applications, réflexion, donnée, Analyse, Diagnostic, tendance, Étude, Hypothèse, Expérimentation, Collecte de données, Tests, Résultats",
   "Étude publiée dans une revue académique sur les effets des pesticides, expérience, pourcentage, analyse, connaissance, source des informations",
   "Document de recherche : analyse de la relation entre la nutrition et la santé mentale, reflexion; résultats attendus, Innovation, Prototype, Solution",

    #Procédure/méthode/guide d'utilisation
    "Ce document décrit la méthode, Étapes, Processus, Séquence, Instructions, Plan, Ordre, Déroulement, Organisation, Flux de travail, Guide pas-à-pas",
    "Guide utilisateur : Exécuter, Appliquer, Suivre, Réaliser, Mettre en œuvre, Vérifier, Compléter, Installer, Configurer, Assurer",
    "Procédure d'audit interne : identification des processus, évaluation des contrôles internes, recommandations d'améliorations",

    #Référentiels
    "Référentiel interne, Norme, Standard, Référence, Directive, Politique, Charte, Référentiel RGPD : gestion des données personnelles, exigences légales",
    "référentiel RGPD, Conformité, Approche, Modèle, Structure, Critères, Implémentation, Adoption, Validation, Suivi, Pilotage, Audit, Contrôle",
    "Référentiel ISO 9001, normes, exigences pour la gestion des processus, Réglementation, Conformité, Certification, Sécurité, Obligations, Responsabilité, Déontologie"
    ]

    labels = [
    "facture", 
    "facture",
    "facture",
    "devis",
    "devis",
    "devis",
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
    "referentiel",
    "referentiel",
    "referentiel"
    ]

    textes_pretraites = [preprocess_text(t) for t in textes]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textes_pretraites)
    classifier = SVC()
    classifier.fit(X, labels)

    base_path = get_base_app_files_path()
    models_path = os.path.join(base_path, 'models')
    os.makedirs(models_path, exist_ok=True)

    # Sauvegarder les fichiers de modèle dans le répertoire models
    joblib.dump(classifier, os.path.join(models_path, "model_svm.joblib"))
    joblib.dump(vectorizer, os.path.join(models_path, "vectorizer_tfidf.joblib"))

    print("\nEntrainement effectue.\n")
