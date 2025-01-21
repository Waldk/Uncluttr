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

    base_path = get_base_app_files_path()
    models_path = os.path.join(base_path, 'models')
    os.makedirs(models_path, exist_ok=True)

    # Sauvegarder les fichiers de modèle dans le répertoire models
    joblib.dump(classifier, os.path.join(models_path, "model_svm.joblib"))
    joblib.dump(vectorizer, os.path.join(models_path, "vectorizer_tfidf.joblib"))

    print("\nEntrainement effectue.\n")
