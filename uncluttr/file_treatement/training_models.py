""" Training models for document classification. """

import os
import json
import nltk
import joblib
from nltk.corpus import stopwords
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.text_preprocessing import preprocess_text
from uncluttr.file_treatement.file_treatement import analyse_fichier


textes = [
    # factures
    "facture numero, client, total : 500 euros, frais de service : 800 euros ht",
    "facture pour services rendus, montant total : 300 euros, tva incluse, ht, montant, frais",
    "facture n 31199, n° de facture : 31199, commande : , tel. : , email : , fax : tva quantite prix de vente unitaire, frais ht unitaire, montant prix de base ht, prix de base ttc, montant ttc en euros 337,00, reglement, carte bancaire, 338,45 €, taux tva ht ttc",
    "facture numero 98765, montant total : 1200 euros, tva a 20%, frais de service 100 euros",
    "facture num 15467, client : societe xyz, montant a regler 2500 euros, conditions de paiement : 30 jours",
    "facture pour produits achetes, montant total : 1000 euros, frais de livraison : 50 euros, tva incluse, echeance : 15/02/2025",
    "facture numero 45678, total : 350 euros, tva : 20%, date limite de paiement : 15/02/2025",
    "facture pour achat de materiels, montant total : 2000 euros ht, frais de port : 50 euros",
    "facture client : entreprise xyz, total ht : 1500 euros, tva : 300 euros, total ttc : 1800 euros",
    "facture numero 56789, reglement par virement bancaire, montant ttc : 1200 euros, echeance : 30 jours",
    "facture num 90876, prestation de service, montant total : 500 euros ht, tva a 10%, frais inclus",
    "facture num 67452, acheteur : entreprise abc, prestation : service de marketing digital pour 3 semaines, montant ht : 2 500 euros, tva : 500 euros, total ttc : 3 000 euros, methode de reglement : virement, date d’emission : 01/01/2025, echeance : 31/01/2025.",
    "facture n 89123, destinataire : societe def, contenu : audit financier et analyse des processus comptables, montant ht : 4 000 euros, tva (10%) : 400 euros, total ttc : 4 400 euros, date d’emission : 05/01/2025, echeance : 04/02/2025, paiement : cheque.",
    "facture num 34567, client : societe ghi, articles : 50 chaises et 10 bureaux, montant ht : 1 200 euros, livraison : 100 euros, tva (20%) : 260 euros, total ttc : 1 560 euros, statut : regle par carte bancaire.",
    "facture numero 11234, societe : sarl jkl, objet : maintenance des equipements reseau, montant ht : 750 euros, tva : 150 euros, total ttc : 900 euros, paiement attendu sous 15 jours.",
    "facture n 65789, entreprise : sci pqr, prestation : formation en gestion de projet (15 participants), montant ht : 2 800 euros, tva (5.5%) : 154 euros, total ttc : 2 954 euros, reglement partiel : 1 500 euros, solde restant : 1 454 euros.",
    "facture numero 98432, client : entreprise lmn, description : creation d’un site web vitrine, montant ht : 3 200 euros, tva (20%) : 640 euros, total ttc : 3 840 euros, echeance : 20/01/2025, statut : non paye.",
    "facture num 75641, destinataire : particulier, prestation : cours particuliers en mathematiques pour 10 seances, montant ht : 500 euros, tva (20%) : 100 euros, total ttc : 600 euros, paiement par especes.",
    "facture n 23698, client : societe uvw, produits : 20 panneaux photovoltaïques, montant ht : 15 000 euros, tva (10%) : 1 500 euros, total ttc : 16 500 euros, statut : livre mais non regle.",
    "facture n 87456, societe : sarl rst, contenu : redaction de contenus seo pour 25 articles, montant ht : 1 800 euros, tva (20%) : 360 euros, total ttc : 2 160 euros, paiement reçu le 10/01/2025.",

    #devis
    "devis num 12345, prix quantite total, 40€, date du devis : 10/12/22, devis, sous total : 160 €, tva (20%) : 32 €",
    "compte client, paiement : par virement bancaire, 30% d'acompte à verser, estimation des couts, validite 1 mois, tva ttc, acompte",
    "devis n 12345, estimation pour travaux, validite, total : 300 euros, tva incluse, offre de prix pour services de reparation, sous-total : 400 euros,",
    "devis n 87456, estimation des travaux : 600 euros, tva incluse, validite 30 jours",
    "devis pour reparation automobile, montant total : 200 euros, tva : 5.5%, duree de validite : 1 mois",
    "devis numero 34298, services de nettoyage, estimation des couts : 350 euros, tva incluse, validite : 15 jours",
    "devis pour prestation de nettoyage, validite : 30 jours, montant total : 750 euros ht",
    "compte client : 00029182, societe : exatdzd, devis n° 12345, estimation pour travaux de renovation, tva incluse : 12 000 euros avec 10% de tva, acompte : 20%",
    "devis pour services de traduction, montant ttc : 1500 euros, duree de validite : 1 mois",
    "devis numero 56789, sous-total : 2500 euros, frais : 200 euros, total ttc : 2700 euros",
    "devis num 1928299 pour remplacement de fenetre au premier etage du batiment, estimation : 600 euros ttc, devis valide pendant 1 mois",
    "devis n 67589, societe : societe ghi, estimation : renovation complete de toiture, total ttc : 7 500 euros, validite : 2 mois, acompte : 30%, delai : avant le 15/03/2025.",
    "devis numero 45789, destinataire : sarl oxy, contenu : demenagement d’un entrepot de 500m², montant ttc : 2 500 euros, validite : 3 semaines, date prevue : 15/02/2025.",
    "devis num 54321, client : particulier, description : construction d’une terrasse en bois de 25m², total ttc : 10 000 euros, validite : 2 mois.",
    "devis n 90234, beneficiaire : sarl pro, prestation : service de traduction pour 50 pages techniques, cout ttc : 1 500 euros, tva incluse, validite : 1 mois.",
    "devis numero 61457, client : sci def, estimation : pose de fenetres pvc double vitrage, total ttc : 6 200 euros, validite : jusqu’au 28/02/2025.",
    "devis num 78965, societe : entreprise lmn, proposition : installation de 10 climatiseurs dans les bureaux, cout ttc : 3 800 euros, tva incluse, validite : 2 mois.",
    "devis n 32564, client : particulier, objet : creation d’une piscine en beton arme, montant ttc : 25 000 euros, acompte : 20%, validite : 6 semaines.",
    "devis numero 19873, beneficiaire : sarl uvw, description : impression de 5 000 flyers a5, cout ttc : 850 euros, validite : 30 jours.",
    "devis num 43567, destinataire : societe tuv, prestation : organisation d’un seminaire d’entreprise pour 50 personnes, montant ttc : 9 500 euros, validite : 1 mois.",

    #contrats
    "contrat, contractant, prestataire, employeur, salarie, partie prenante, signataire, donneur d’ordre, sous-traitance",
    "accord, prestations, services, obligations, terme, periode d’essai, resiliation, renouvellement, delai, echeance, rupture anticipee, clause resolutoire, clause penale, indemnite",
    "contrat de prestation de services entre la societe abc et le client xyz, duree : 12 mois, montant global : 10000 euros",
    "contrat de travail salarie en cdi, periode d'essai de 3 mois, salaire brut mensuel : 2200 euros, renouvellement du contrat",
    "accord de prestatation, le prestataire durant sa mission devra suivre les regles de gestion et de securite de l'entreprise, obligations des parties, duree de validite : 2 ans",
    "contrat d'alternance, alternant : camille claudel, duree : 12 mois, montant total : 5000 euros",
    "contrat de location, locataire : jean dupont, proprietaire : pierre martin, duree : 1 an, montant mensuel : 800 euros",
    "accord de confidentialite entre entreprise a et entreprise b, duree de validite : 3 ans",
    "contrat de professionalisation en cdd, periode d'essai : 2 mois, salaire brut mensuel : 2500 euros",
    "contrat commercial pour fourniture de materiels, montant total : 10 000 euros, echeance : 6 mois, rupture de contrat anticipee",
    "contrat de stage, stagiaire : coline jean, stage non remunere de 2 mois, obligation de respect des regles",
    "contrat de travail cdi, salarie : jean dupont, poste : chef de projet, duree : 35 heures par semaine, remuneration : 3 500 euros brut mensuel, debut du contrat : 01/02/2025, lieu : paris.",
    "contrat de travail cdd, salarie : marie lefevre, poste : assistante de direction, duree : 6 mois, remuneration : 2 200 euros brut mensuel, debut du contrat : 15/03/2025, lieu : lyon.",
    "contrat de prestation de services, prestataire : sarl tech solutions, prestation : developpement d’un site e-commerce, montant : 15 000 euros, duree : 3 mois, delai de livraison : 31/05/2025.",
    "contrat de location commerciale, locataire : societe abc, bien loue : boutique de 100m², loyer mensuel : 1 800 euros, duree : 3 ans, depot de garantie : 2 mois de loyer.",
    "contrat de partenariat, entreprise : societe def, partenaire : entreprise xyz, objet : fourniture de services de traduction, duree : 1 an, montant total : 50 000 euros.",
    "contrat d’embauche pour un freelance, prestataire : paul martin, mission : creation de contenu pour blog, remuneration : 1 000 euros par mois, duree : 6 mois.",
    "contrat de vente d’immobilier, vendeur : societe lmn, acheteur : m. dupuis, bien vendu : appartement 2 pieces, prix de vente : 150 000 euros, date de signature : 10/01/2025.",
    "contrat de maintenance informatique, prestataire : societe tuv, client : entreprise ghi, prestation : entretien du parc informatique, duree : 12 mois, montant annuel : 10 000 euros.",
    "contrat de sous-traitance, entreprise : societe xyz, sous-traitant : sarl abc, prestation : gestion de la logistique, montant : 50 000 euros sur 12 mois.",

    # bons de commande
    "bon de commande numero 5678, fournisseur : abc corp, articles : 10",
    "commande passee le 12 janvier, produits : fournitures de bureau, reference : 018273781, quantite : 50",
    "bon de commande num 14578, fournisseur : entreprise abc, produit commande : papier, quantite : 100",
    "commande effectuee le 10 janvier, produit : ordinateurs portables, quantite : 5, date de livraison prevue : 15 janvier",
    "bon de commande numero 24567, fournisseur : tech corp, articles : 20, montant total : 2000 euros",
    "bon de commande n 12345, date : 10 janvier, fournisseur : entreprise xyz, produits : fournitures de bureau, ref : Y28ZY2U1, quantite : 50",
    "commande passee le 18/07/2024, produit : machines de decapage, quantite : 10, montant total : 8000 euros",
    "bon de commande numero 67890, articles : 30, total : 1500 euros ht, frais de port : 100 euros",
    "bon de commande num 45678, fournisseur : societe abc, produits commandes : fournitures informatiques, total : 2500 euros ttc",
    "commande effectuee le 05/03, produit : imprimantes, ref : EPSON 28718, quantite : 5, montant ttc : 2500 euros",
    "commande passee le 17 janvier 2024, reference du produit : 000182891TTE, quantite commandee : 78 unites, 32517 euros, 20% de tva",
    "bon de commande numero 12345, fournisseur : societe def, articles : 30 chaises et 10 bureaux, montant ttc : 3 000 euros, date : 20/01/2025.",
    "bon de commande n 98765, client : entreprise abc, service : audit des systemes d’information, cout ttc : 4 500 euros, paiement : virement, livraison : 31/01/2025.",
    "bon de commande n 34567, prestataire : entreprise ghi, articles : installation de cameras de surveillance, cout ttc : 6 500 euros, date de livraison : 25/01/2025.",
    "commande passee le 10 avril 2024,numero 188SJ2901, client : sci lmn, description : construction d’une mezzanine industrielle, total ttc : 20 000 euros, acompte demande : 30%.",
    "bon de commande num 45678, societe : particulier, produits : achat de panneaux solaires, total ttc : 12 000 euros, statut : confirme.",
    "bon de commande numero 90234, fournisseur : societe tuv, objet : livraison de 100 chaises pliantes pour evenement, cout ttc : 1 200 euros.",
    "bon de commande n 14321, client : sarl abc, articles : 20 imprimantes multifonctions, montant ttc : 10 000 euros, paiement sous 30 jours.",
    "bon de commande num 31456, destinataire : sci def, service : renovation des espaces communs d’un immeuble, montant ttc : 8 000 euros, delai : 2 mois.",
    "commande passee le 30/10/2024, numero 78123, entreprise : societe xyz, contenu : installation d’un reseau informatique complet, cout ttc : 15 000 euros, livraison attendue : 15/02/2025.",

    # fiches de paie
    "fiche de paie, employe : jane doe, salaire : 3000 euros ht, montant, poste, horaire",
    "bulletin de salaire : periode d'emploi du 1er au 31 mars, net a payer : 2500 euros, date de paiement, taux horaire : 28 euros/heure",
    "date de paiement, matricule, n° siret: n° ape:, impot sur le revenu base montant, date designation base, part employe, taux montant, employeur, montant, travail incident, net a payer, affectation : , poste : , emploi ncc :, horaire mensuel 156,00, debut contrat : , d. anciennete : , 01 2024, brut ss 3076,10 10167,22, brut imposable, net fiscal 2805,36 9839,36, cotisations salariales, cotis. patronales, total verse employeur, hs/hc exo fiscales, droit pris solde, conges payes, net a payer avant impot sur le revenu, montant net social, virement, exoneration de cotisations salariale, impot sur le revenu preleve a la source, autres retenues, donnees fiscales, traitements et salaires, hs/hc exonerees",
    "fiche de paie mois de janvier, salarie : pierre dupont, salaire brut : 2500 euros, net a payer : 2000 euros",
    "bulletin de salaire : employe : jean martin, periode de travail du 1er au 31 decembre, net a payer : 1800 euros, charges patronales : 1900 euros",
    "fiche de paie de mai, montant brut : 3000 euros, cotisations sociales : 600 euros, net imposable : 2400 euros",
    "fiche de paie mois de aout, employe : jean martin, brut : 3000 euros, net a payer : 2400 euros",
    "bulletin de salaire, periode d'emploi : 1er au 31 mars, brut : 2500 euros, cotisations : 500 euros, prime accordee : 1890 euros",
    "fiche de paie salarie : pierre dupont, brut mensuel : 2800 euros, cotisations salariales : 600 euros, net imposable : 2200 euros",
    "bulletin de salaire mois de fevrier, employe : anna dupont, net a payer : 2100 euros, date de paiement : 28/02/2025",
    "fiche de paie, salaire brut : 3200 euros, poste : cadre, cotisations patronales : 1000 euros, net fiscal : 2700 euros",
    "bulletin de salaire de jean dupont, salaire brut : 3 500 euros, salaire net : 2 700 euros, cotisations sociales : 800 euros, prime de performance : 300 euros, date de paiement : 31/01/2025.",
    "fiche de paie de marie lefevre, salaire brut : 2 200 euros, salaire net : 1 750 euros, cotisations sociales : 450 euros, bonus de fin d’annee : 200 euros.",
    "fiche de paie mois de mars, salaire brut : 5 000 euros, salaire net : 3 800 euros, cotisations sociales : 1 200 euros, heures supplementaires : 300 euros.",
    "fiche de paie de sophie moreau, salaire brut : 2 800 euros, salaire net : 2 200 euros, cotisations sociales : 600 euros, prime de deplacement : 150 euros.",
    "fiche de paie de marc lefevre, salaire brut : 3 200 euros, salaire net : 2 500 euros, cotisations sociales : 700 euros, bonus commercial : 400 euros.",
    "fiche de paie de clara dubois, salaire brut : 4 000 euros, salaire net : 3 100 euros, cotisations sociales : 900 euros, heures supplementaires : 200 euros.",
    "bulletin de salaire de julien lefevre, salaire brut : 3 500 euros, salaire net : 2 600 euros, cotisations sociales : 900 euros, prime de fin d’annee : 300 euros.",
    "fiche de paie de fevrier, salaire brut : 1 800 euros, salaire net : 1 400 euros, cotisations sociales : 400 euros, prime de formation : 150 euros.",
    "fiche de paie de paul martin, salaire brut : 4 500 euros, salaire net : 3 600 euros, cotisations sociales : 900 euros, primes : 500 euros.",

    # articles de presse
    "article de presse, critique, point de vue, editorial, chronique, source, citation, reporteur, journaliste, agence de presse, titre, accroche, , sujet d’actualite, contexte, enjeu",
    "dans un article publie recemment, information, temoignage, enquete, reportage, declaration, annonce, revelation, debat, controverse",
    "faits divers, politique, societe, economie, environnement, technologie, sante, culture, sport, international, interview",
    "progres dans le traitement des maladies neurodegeneratives grace aux therapies genetiques, article sur l'impact du changement climatique sur l'environnement, analyse des effets des catastrophes naturelles",
    "reportage sur l'actualite politique, entretien avec le ministre de l'interieur, commentaires sur la situation actuelle, qu'est-ce que l'énergie nucléaire et comment est-elle utilisée ?",
    "article dans un quotidien national, sujet d'actualite : crise economique, repercussions sur le marche du travail",
    "decouverte scientifique : developpement d'une batterie ultra-rapide, impact sur l'industrie automobile",
    "enquete sur les conditions de travail dans les usines de production en asie, les defis et opportunites de l'inclusion sociale pour les populations vulnerables",
    "etude sur l'influence des cultures africaines dans l'art contemporain, analyse historique de la construction de grandes villes comme paris et londres",
    "crise economique mondiale : causes, consequences et strategies de redressement, les revolutions technologiques de l'antiquite a nos jours, de la roue a internet",
    "les defis et opportunites de l'inclusion sociale pour les populations vulnerables, decouvertes archeologiques recentes dans les anciennes civilisations mesoamericaines", 
    "enquete sur la corruption dans les marches publics, temoignages et preuves, investigation sur les pratiques des grands groupes technologiques concernant la vie privee",
    "nouveaux materiaux revolutionnaires dans l'industrie du batiment, reduction de l'empreinte carbone. article sur les tendances litteraires actuelles, emergence de nouveaux auteurs",
    "evolution des crypto-monnaies en 2025, tendances et opportunites d'investissement. impact des nouvelles reglementations bancaires sur les startups fintech",
    "impact des nouvelles decouvertes en physique quantique sur les technologies futures, progres dans le traitement des maladies neurodegeneratives grace aux therapies genetiques",
    "le fonctionnement des fusees spatiales explique en termes simples. comment les vaccins sont developpes, etapes cles et defis ?",
    "initiatives locales pour la preservation des forets tropicales, projets de restauration des barrieres de corail endommagees dans le monde",
    "histoire des grandes routes commerciales a travers le monde, de la route de la soie au commerce maritime",
    "evolution des normes vestimentaires et leur influence sur la societe moderne",
    "changement des dynamiques familiales avec l'essor du travail a distance. solutions innovantes pour la gestion des dechets plastiques a grande echelle",

    # recherches sur un sujet
    "recherche scientifique sur l'intelligence artificielle et ses applications, reflexion, donnee, analyse, diagnostic, tendance, etude, hypothese, experimentation, collecte de donnees, tests, resultats",
    "etude publiee dans une revue academique sur les effets des pesticides, experience, pourcentage, analyse, connaissance, source des informations",
    "document de recherche : analyse de la relation entre la nutrition et la sante mentale, reflexion; resultats attendus, innovation, prototype, solution",
    "etude sur l'impact des reseaux sociaux sur la sante mentale des adolescents, methodologie, resultats preliminaires",
    "recherche scientifique sur la bioethique, analyse des enjeux juridiques et sociaux, etude comparee internationale, impact des vaccins a ARN messager sur la prevention des maladies infectieuses",
    "analyse des tendances dans les technologies de l'information et leur evolution au cours des 20 dernieres annees, les recherches ont mene à la conclusion que plusieurs solutions etaient envigasables",
    "analyse des effets des feux de foret sur la qualite de l'air en milieu urbain et impact des microplastiques sur les ecosystemes aquatiques et leurs habitants",
    "etude sur les algorithmes de machine learning pour la reconnaissance faciale, recherche sur les effets des mouvements sociaux sur les legislations internationales",
    "recherche sur l'efficacite des plateformes d'apprentissage en ligne pour les adultes, statistiques permettant de mettre en evidence l'efficacite de la solution",
    "analyse des influences interculturelles dans l'architecture urbaine moderne, apres de nombreuses recherches et temoignages receuillis, nous pouvons assurer que les differentes cultures et epoques influent sur la societe actuelle",
    "etude comparative des politiques energetiques en europe et en asie, document de recherche sur les interactions entre les changements culturels et les technologies emergentes",
    "recherche sur les consequences a long terme des infections respiratoires chez les enfants, les recherches ont montre qu'un taux important de dioxygene influaient beaucoup l'apparition de la maladie",
    "analyse des strategies de reforestation dans les regions semi-arides, de nombreux projets pour la reforestation ont ete menes. voyons maintenant si l'impact a ete positif ou pas",
    "etude comparative des performances des batteries lithium-ion et lithium-soufre, en comparant plusieurs des caracteristiques propres aux batteries, nous pouvons en deduire que cette batterie est mieux en tout point",
    "analyse des comportements d'achat en ligne chez les differentes generations, on constate que les habitudes d'achat changent avec le temps et la mode de consommation egalement",
    "impact des politiques fiscales sur les investissements dans les start-ups. pour conclure, les micro-entreprises subissent enormement de la politique fiscale selon les chiffres vus dans ce developpement",
    "recherche sur l'evolution des traditions musicales dans les societes globalisees. en effet, selon les statistiques et les chiffres pre-etablies, les genres musicaux evoluent au fil des ans ",
    "etude sur l'efficacite des legislations contre la cybercriminalite. d'apres un precedent rapport redige par l'anssi, expert dans le domaine en france, nous pouvons en deduire qu'il reste des progrets a faire dans ce domaine",
    "impact des fermes solaires sur les habitats terrestres et leurs ecosystemes. selon les experts dans ce domaine, les fermes solaires ont beaucoup d'avantages et permettent notamment de produire de l'energie verte",
    "impact des crises sanitaires sur les politiques economiques et sociales, les resultats des etudes sur le sujet indiquent que les crises sanitaires sont l'element declancheur de potitique nefaste",

    #procedure/methode/guide d'utilisation
    "ce document decrit la methode, etapes, processus, sequence, instructions, plan, ordre, deroulement, organisation, flux de travail, guide pas-a-pas",
    "guide utilisateur : executer, appliquer, suivre, realiser, mettre en œuvre, verifier, completer, installer, configurer, assurer",
    "procedure d'audit interne : identification des processus, evaluation des controles internes, recommandations d'ameliorations",
    "guide utilisateur pour installation d'un logiciel de gestion de projet, etapes detaillees et precautions a prendre",
    "procedure de verification des comptes financiers, etapes cles pour auditer les documents comptables",
    "methode pour la gestion du temps dans une equipe de travail, planification des tâches et des priorites",
    "methode pour evaluer les performances des employes et fixer des objectifs annuels, etapes pour l'organisation d'une reunion de service : preparation, convocation, compte rendu",
    "guide pas-a-pas pour la mise a jour du firmware sur les appareils connectes, methode pour configurer une imprimante reseau et resoudre les problemes courants",
    "guide pour former les operateurs sur les nouvelles machines de production, etapes pour gerer les dechets industriels selon les normes environnementales",
    "methode pour etablir un budget previsionnel annuel et suivre son execution, procedure de preparation et de soumission des declarations fiscales",
    "procedure pour activer un compte utilisateur sur une application mobile, guide pas-a-pas pour parametrer un smartphone pour la premiere utilisation", 
    "procedure pour soumettre une demande de remboursement des frais professionnels. methode pour la gestion des archives administratives, tri et destruction des documents perimes",
    "procedure de declaration des heures supplementaires pour les employes. guide utilisateur pour la mise a jour des donnees personnelles sur le systeme rh",
    "etapes pour effectuer une sauvegarde des donnees sur le serveur interne. procedure pour verifier et valider les factures des fournisseurs",
    "methode pour elaborer un plan de projet : identification des objectifs et ressources. etapes pour creer un calendrier de travail et suivre les delais",
    "guide pour former les agents a la gestion des appels telephoniques entrants. etapes pour documenter un incident signale par un client",
    "procedure pour steriliser les instruments chirurgicaux selon les normes en vigueur. guide pour remplir et envoyer un dossier medical numerique",
    "procedure pour evaluer les connaissances des eleves apres une session de formation. methode pour organiser un atelier interactif en utilisant des outils numeriques",
    "methode pour nettoyer et entretenir les appareils electromenagers. etapes pour recharger une voiture electrique en toute securite",
    "methode pour analyser les risques dans un projet et definir des strategies de mitigation. procedure pour assurer la maintenance preventive des equipements industriels",

    #referentiels
    "referentiel interne, norme, standard, reference, directive, politique, charte, referentiel rgpd : gestion des donnees personnelles, exigences legales",
    "referentiel interne pour la gestion des audits financiers, calendrier annuel et roles des parties impliquees",
    "referentiel iso 9001, normes, exigences pour la gestion des processus, reglementation, conformite, certification, securite, obligations, responsabilite, deontologie",
    "norme interne pour la formation des equipes de support client, regles de communication et gestion des objections",
    "referentiel rgpd, obligations pour les entreprises traitant des donnees personnelles, guide de mise en conformite",
    "referentiel interne pour la gestion des risques, evaluation des menaces, plan de reduction des risques",
    "referentiel pour la gestion des competences, classification des postes, criteres d'evaluation et plans de formation",
    "norme interne pour la validation des achats, procedure de demande d'achat et validation par niveau hierarchique",
    "norme operationnelle pour l'entretien des equipements, calendrier de maintenance preventive et reactive",
    "referentiel pour la gestion des partenaires externes, regles de collaboration et clauses de confidentialite",
    "referentiel pour la gestion des evaluations annuelles, methodologie, objectifs et criteres de performance",
    "referentiel rh interne, politique de recrutement, processus de selection, grille salariale et avantages sociaux",
    "referentiel interne sur la sante et securite au travail, mesures de prevention et regles d'hygiene",
    "referentiel sur le controle des couts, optimisation des depenses et analyse des ecarts budgetaires. evaluation des risques et retour sur investissement",
    "referentiel pour la gestion des stocks, seuils de reapprovisionnement, rotation des produits et inventaire annuel",
    "norme interne pour la gestion de la qualite, procedure de controle et resolution des non-conformites. regles de gestion des transports et suivi des livraisons",
    "referentiel pour la gestion des contrats client, suivi des renouvellements et clauses de resiliation",
    "norme interne pour la formation des equipes de support client, regles de communication et gestion des objections",
    "norme interne pour la planification strategique, definition des objectifs a moyen et long terme. identification des vulnerabilites et mise en place de plans de mitigation",
    "referentiel sur la strategie de developpement durable, plans d'action et suivi des indicateurs environnementaux",

    #attestations
    "vos prestations caf, emplacement reserve a la caf, madame eva supiot, 9 rue boulard, 75014 paris, 751, le 19/08/2022, 06764281041100000000, attention : vous avez l’obligation de nous signaler immediatement tout changement de situation, (familial, professionnel, logement .). n° dossier : 0676428 q, nous contacter :, nous telephoner : 3230, nous ecrire : caf de paris, 75656 paris cedex 13, tous nos contacts sur caf.fr, attestation de paiement, le directeur de la caf de paris certifie que :, eva supiot, nee le 22/03/2002 a perçu les prestations suivantes pour le mois de juillet 2022 : prestations montant, allocation de logement 210,00 €, quotient familial, juillet 2022 : 109 €, n attestation delivree compte tenu des informations connues a ce jour par la caf de paris. les prestations versees par la caisse d'allocations familiales sont insaisissables sauf pour le paiement des dettes alimentaires.",
    "je soussigne eva supiot demeurant a 9, rue boulard 75014 paris ne le 22/03/2002 a chatenay malabry confirme participer au sejour reserve a les arcs du 22/03/2025 au 28/03/2025 et atteste que les pieces justificatives transmises a l'appui de la reservation faite dans le cadre du programme depart 18:25 refletent bien ma situation, j'ai connaissance qu'une fausse attestation de ma part, m'exposerait a des sanctions penales prevues et reprimees par les articles 441-1 et suivants du code penal. est puni d'un an d'emprisonnement et de 15 000 euros d’amende le fait d'etablir une attestation ou un certificat faisant etat de faits materiellement inexacts, des controles de la veracite et de l'exactitude des informations declarees et pieces justificatives transmises seront susceptibles d'etre realises ulterieurement, fait le 18/11/2024 a (lieu) : paris, signature :",
    "attestation de presence, certifie la participation a un seminaire professionnel, validite : 2 jours",
    "je soussigne jean michel certifie avoir effectue le stage de formation sur la gestion des risques, lieu : paris",
    "attestation de residence, confirme par le maire de la commune, document signe et valide",
    "attestation de presence, je certifie avoir pris part au seminaire professionnel, qui s'est deroule le 08/03/2024, a Paris",
    "je soussigne pierre dupont, atteste avoir effectue une formation sur la gestion des risques",
    "attestation de residence, document valide par le maire, confirme l'adresse du resident",
    "je soussigne claire martin, certifie participer a la conference sur les innovations technologiques",
    "attestation de stage, certifie que l'etudiant a complete un stage de 3 mois en entreprise",
    "attestation d'assurance, scolaire et extra-scolaire le 18 juillet 2023, madame, monsieur, nous certifions que eva supiot beneficie d’un contrat d.assurance scolaire. periode de validite : annee scolaire 2023/2024, l’eleve designe ci-dessus beneficie des garanties suivantes : responsabilite civile vie privee, individuelle accident corporel : indemnite en cas de deces ou invalidite permanente, assistance 24h/24 . tel. 01 55 92 26 92, la presente attestation ne peut engager l.assureur en dehors des limites prevues pour les clauses et conditions du contrat auxquelles elle se refere. fait a yerres, le 18/07/2023, guillaume borie, directeur general delegue",
    "attestation d’emploi de jean dupont, societe : xyz, poste : directeur marketing, duree : cdi, date d’embauche : 01/01/2020, fonction : gestion d’equipe, salaire brut mensuel : 3 500 euros.",
    "attestation de travail de marie lefevre, societe : abc, poste : assistante comptable, periode d'emploi : 01/02/2024 a 31/01/2025, salaire brut mensuel : 2 200 euros.",
    "attestation de stage de pierre roussel, entreprise : societe lmn, duree du stage : 6 mois, poste : analyste financier, periode : du 01/09/2024 au 28/02/2025.",
    "attestation de paiement de salaire de sophie moreau, societe : abc, salaire verse en janvier 2025, montant brut : 2 800 euros, montant net : 2 200 euros.",
    "attestation de residence de marc lefevre, adresse : 12 rue des champs, 75012 paris, duree de residence : depuis le 01/01/2020.",
    "attestation de prise de conges de clara dubois, periode : du 10/01/2025 au 20/01/2025, duree totale : 10 jours, approuve par la direction.",
    "attestation de presence de julien lefevre, entreprise : xyz, presence continue depuis le 01/06/2018, fonction : responsable commercial.",
    "attestation de salaire de anne dupuis, societe : rst, salaire brut pour le mois de janvier 2025 : 1 800 euros.",
    "attestation de conformite de paul martin, entreprise : lmn, produits livres et installes conformement au contrat du 15/12/2024.",

    #cv
    "cv, experience professionnelle : assistant commercial chez xyz entreprise, gestion des relations clients et suivi des commandes",
    "competences : maitrise de excel, word, et powerpoint, langues : anglais courant, espagnol intermediaire",
    "parcours professionnel : technicien informatique chez abc tech, installation et maintenance de reseaux",
    "diplome : master en gestion de projet obtenu a l'universite de paris en 2020",
    "formation continue : certification en marketing digital suivie en 2023",
    "stage : stage en ressources humaines chez entreprise xyz, gestion des recrutements et integration des nouveaux employes",
    "loisirs et interets : passion pour la photographie, membre d'un club de randonnee",
    "experience : responsable logistique chez entreprise abc, supervision des flux de marchandises et gestion des stocks",
    "competences : programmation en python et java, connaissances en intelligence artificielle",
    "langue maternelle : francais, niveau avancé en italien, notions de mandarin",
    "Formation, autres activités, expérience professionnelle, 2020 – 2025, ece ecole d'ingénieurs, programme grande ecole spécialisation systèmes d’information et cybersécurité, 2020 - baccalauréat scientifique mention très bien, eva supiot, apprentie ingénieure, recherche des missions dans les domaines des systèmes d’information et de la cybersécurité, ski en compétition, danse classique, robotique, arts plastiques, développement durable, 2021-2022 responsable potager – noise paris, 75015, 2022 stagiaire développeur – polytechnique palaiseau, 91120, tests fonctionnels et techniques relecture de code applicatif, initiation aux logiciels sonar, gitlab, selenium, découverte des métiers de la dsi (5 semaines) 2021emploi saisonnier - un autre regard opticien gif-sur-yvette, 91190, gestion des stocks, mise en place des produits, administratif (gestion des dossiers mutuelles et retour des pièces défectueuses), petites réparations.(1 mois), nationalité française, verrières-le-buisson, 91370, 2020-2022, projets en équipe - ece parisparis, compétences competences it : langage c et c++ avec allegro 4, proteus, arduino, pack office, langage vhdl, langues : anglais (niveau b2), espagnol (niveau a2)",
    "cv de jean dupont, candidat pour un poste de directeur marketing, experience : 5 ans chez xyz, competences : gestion de projet, analyse de donnees, langues parlees : anglais et espagnol, diplome : master en marketing digital.",
    "cv de marie lefevre, chercheuse en biotechnologie, experience : 3 ans dans un laboratoire de recherche, competences : analyse moleculaire, gestion d’equipes de recherche, diplome : doctorat en biologie.",
    "cv de paul martin, candidat pour un poste de developpeur web, experience : 4 ans de developpement php et javascript, competences : conception d'applications web, maitrise de git, diplome : licence en informatique.",
    "cv de clara dubois, candidate pour un poste de chef de projet it, experience : 6 ans dans la gestion de projets digitaux, competences : gestion de budget, communication avec les clients, diplome : master en management de projets.",
    "cv de pierre roussel, candidat pour un poste de commercial, experience : 8 ans dans la vente b2b, competences : negociation, prospection, gestion de la relation client, diplome : bts en commerce.",
    "cv de sophie moreau, candidate pour un poste de designer graphique, experience : 4 ans dans une agence de design, competences : photoshop, illustrator, creation de chartes graphiques, diplome : licence en design graphique.",
    "cv de marc lefevre, candidat pour un poste de consultant en ressources humaines, experience : 5 ans dans le conseil en recrutement, competences : gestion des talents, gestion de la performance, diplome : master en rh.",
    "cv de anne dupuis, candidate pour un poste de comptable, experience : 3 ans dans un cabinet d’expertise comptable, competences : comptabilite analytique, fiscalite, gestion de la paie, diplome : bts comptabilite et gestion.",
    "cv de julien lefevre, candidat pour un poste de responsable logistique, experience : 7 ans dans la gestion de stocks, optimisation des flux, competences : gestion de la chaine d'approvisionnement, diplome : dut en gestion des entreprises.",


    #bons de livraison
    "bon de livraison numero 3456, client : entreprise abc, adresse : 45 rue du commerce, articles : 10",
    "produits livres : meubles de bureau, quantite : 5, date de livraison : 10/01/2025",
    "bon de livraison num 5678, fournisseur : xyz corp, adresse de livraison : 23 avenue des champs, paris",
    "commande n 12345, date de livraison : 15/02/2025, articles : 3, description : ordinateurs portables",
    "bon de livraison : produits alimentaires, quantite : 20, client : supermarche beta, date : 25/01/2025",
    "fournisseur : entreprise abc, articles livres : fournitures scolaires, quantite totale : 100",
    "livraison partielle de la commande n 9876, produits : chaises de conference, quantite : 50, restant : 20",
    "client : entreprise xyz, adresse de livraison : 12 rue des roses, ville : lyon, code postal : 69000",
    "bon de livraison n 4321, produit : imprimante laser, quantite : 1, accessoires : cartouches d'encre, date : 22/01/2025",
    "articles livres : logiciels de gestion, cle usb, manuel utilisateur, date : 18/01/2025, client : universite alpha",
    "fournisseur : entreprise delta, commande numero 4567, articles : ecrans plats, quantite : 10, livraison le 20/01/2025",
    "bon de livraison num 56478, client : entreprise uvw, contenu : 20 panneaux solaires, date de livraison : 15/01/2025.",
    "bon de livraison n 19876, destinataire : sarl jkl, produits : 10 armoires metalliques, livraison effectuee : 12/01/2025.",
    "bon de livraison numero 34587, client : societe def, contenu : ordinateurs portables, total ttc : 15 000 euros, date : 10/01/2025.",
    "livraison partielle de la commande n 56432, beneficiaire : sarl oxy, articles : 5 climatiseurs, statut : livre et accepte.",
    "bon de livraison num 98732, societe : sci pqr, service : pose de fenetres double vitrage, date prevue : 18/01/2025.",
    "bon de livraison numero 45321, destinataire : societe tuv, produits : systeme audio pour salle de conference, valeur ttc : 5 000 euros.",
    "bon de livraison n 31245, client : entreprise lmn, contenu : fournitures de bureau (100 unites), date : 08/01/2025.",
    "bon de livraison numero 14789, beneficiaire : sci def, livraison : meubles de bureau (10 armoires), statut : reception confirmee.",
    "livraison de la commande numero 90876, societe : particulier, articles : meubles de cuisine, date : 20/01/2025, observation : un meuble endommage.",


    #cahier des charges
    "cahier des charges pour le developpement d'une application mobile de gestion des taches, sections : objectifs, cible utilisateur, specifications fonctionnelles, contraintes techniques, planning de livraison.",
    "specification fonctionnelle pour la conception d'un site e-commerce, details : systeme de paiement, gestion du catalogue produit, suivi des commandes, contraintes legales rgpd.",
    "document de specifications pour un systeme de gestion des ressources humaines, contenu : gestion des conges, suivi des evaluations, rapports d'activite, integration avec le crm.",
    "cahier des charges pour la mise en place d'un outil de support client, modules : chat en ligne, base de connaissances, reporting des performances.",
    "specifications techniques pour un projet de refonte du site internet corporate, points : responsive design, optimisation seo, integration des contenus existants.",
    "document de cadrage pour un projet de migration vers le cloud, besoins : reduction des couts, securite des donnees, compatibilite avec les systemes existants.",
    "cahier des charges pour l'implementation d'un outil de business intelligence, fonctionnalites : tableaux de bord, exploration de donnees, automatisation des rapports.",
    "document de specifications fonctionnelles pour le developpement d'un logiciel de gestion de projet, besoins : collaboration en temps reel, gestion des taches, reporting.",
    "description des besoins pour un systeme de reservation en ligne, inclus : gestion des disponibilites, interface utilisateur, notifications par email.",
    "cahier des charges pour un projet de mise en place d'une strategie de marketing digital, sections : campagnes seo, publicite ppc, generation de leads.",
    "specifications pour un projet d'automatisation des processus administratifs, objectifs : gain de temps, reduction des erreurs humaines, cout estime.",
    "document de specifications pour le design d'une plateforme collaborative, contenu : gestion des utilisateurs, partage de fichiers, historique des modifications.",
    "cahier des charges pour la creation d'une application mobile pour la gestion des stocks, contraintes : support ios et android, synchronisation temps reel.",
    "plan de projet pour un outil de suivi des performances des employes, details : objectifs de suivi, generation de rapports automatiques, analyse des donnees.",
    "document d'expression des besoins pour la creation d'une plateforme de formation en ligne, inclut : gestion des utilisateurs, cours interactifs, certification.",
    "cahier des charges pour un outil de suivi de projet agile, fonctionnalites : gestion de backlog, tableau kanban, rapports d'avancement.",
    "specifications pour un outil de facturation automatisee, details : generation de factures pdf, integration bancaire, suivi des paiements.",
    "document de definition des besoins pour un projet de digitalisation des processus financiers, contenu : flux de validation, suivi des depenses, audits.",
    "cahier des charges pour un portail client, sections : tableau de bord personnalise, communication directe, gestion des demandes.",
    "plan fonctionnel pour la mise en place d'un crm sur mesure, inclut : gestion des leads, suivi des opportunites, personnalisation par utilisateur.",

    #document d'architecture technique
    "document d'architecture systeme pour un projet de migration vers aws, inclut : diagrammes d'infrastructure, composants principaux, details de securite.",
    "schema technique pour l'integration d'un erp, contenu : interconnexions entre les modules, api utilisees, contraintes de performance.",
    "plan d'architecture pour une plateforme cloud native, inclut : microservices, orchestrateur kubernetes, systeme de monitoring.",
    "document d'infrastructure technique pour un projet d'hyperconvergence, details : stockage, reseaux, compute, haute disponibilite.",
    "architecture technique pour un systeme de sauvegarde et restauration de donnees, inclut : planning, encryption, systeme de logs.",
    "rapport technique sur le design d'une architecture serverless, sections : lambda functions, securite des endpoints, optimisation des couts.",
    "document de conception d'un systeme de gestion des fichiers, details : structures des donnees, protocols de transfert, sauvegardes automatiques.",
    "architecture technique pour un outil d'analyse de donnees en temps reel, contenu : pipeline de donnees, systeme de stockage, reporting.",
    "rapport d'architecture technique pour la refonte d'une application legacy, inclut : compatibilite ascendante, migration des donnees, plan de deploiement.",
    "guide d'implementation d'une architecture big data, sections : sources de donnees, systeme de traitement, stockage scalable.",
    "design technique pour une plateforme de streaming video, contenu : encodage, mise en cache, distribution des flux.",
    "architecture de securite pour une application bancaire, inclut : chiffrement, gestion des identites, logs des transactions.",
    "documentation technique pour un systeme de gestion des acces, contenu : authentification unique, roles et permissions, audits.",
    "schema d'architecture pour un projet d'ia, inclut : modeles d'apprentissage, bases de donnees, systeme de deploiement.",
    "plan technique pour un projet de blockchain, contenu : structure des blocs, consensus, gestion des cles privees.",
    "guide d'architecture pour un systeme de messagerie instantanee, sections : protocoles de communication, stockage des messages, notifications push.",
    "document d'infrastructure pour un projet de containerisation, inclut : plan de deploiement, orchestration, systemes de monitoring.",
    "diagramme technique pour un systeme de sauvegarde distribuee, contenu : replication, tolerances aux pannes, systemes de controle.",
    "rapport d'architecture pour une plateforme de gestion des ressources humaines, inclut : modeles de donnees, flux de travail, acces utilisateurs.",
    "design d'un systeme distribue pour la gestion des flux financiers, contenu : interconnexions, securite, gestion des performances.",

    #compte-rendu de reunion
    "compte rendu de la reunion hebdomadaire d'equipe, points abordes : priorites de la semaine, mise a jour des projets, discussion des obstacles.",
    "rapport de reunion de suivi client, contenu : progression du projet, retour du client, prochaines etapes, responsabilites des membres.",
    "synthese de reunion pour un projet agile, sujets : revision du sprint precedent, definition des objectifs du sprint actuel, feedback.",
    "compte rendu de reunion strategique, themes : analyse de la concurrence, plan marketing, allocation des budgets.",
    "rapport de reunion technique, discussions : choix des technologies, resolution de problemes techniques, deadlines mises a jour.",
    "document de synthese pour une reunion de crise, sujets : identification du probleme, solutions proposees, plan d'action immediat.",
    "compte rendu de la reunion mensuelle du comite de direction, details : revue des performances, initiatives strategiques, priorites a venir.",
    "rapport de reunion avec un prestataire, contenu : etat d'avancement des livrables, ajustements demandes, planning mis a jour.",
    "compte rendu de brainstorming sur un nouveau produit, points : idees proposees, analyses preliminaires, actions de suivi.",
    "resume de reunion d'avancement sur un chantier, details : etat des travaux, problemes rencontres, dates de livraison estimees.",
    "rapport de reunion sur l'amelioration des processus internes, discussions : goulots d'etranglement, solutions techniques, objectifs.",
    "document de suivi pour une reunion avec un fournisseur, contenu : renegociation des termes, qualite des produits, prochaines livraisons.",
    "compte rendu de reunion d'equipe commerciale, sujets : objectifs trimestriels, resultats des ventes, feedback terrain.",
    "resume de reunion pour un projet de r&d, contenu : etat des recherches, besoins en materiel, contraintes budgetaires.",
    "rapport de reunion pour la mise en place d'un nouvel outil, discussions : formation des utilisateurs, adoption, retour d'experience.",
    "compte rendu de reunion pour la redaction d'une proposition commerciale, points : contenu de l'offre, delais de soumission, roles.",
    "resume de reunion pour le lancement d'une campagne publicitaire, discussions : messages cles, choix des canaux, budget.",
    "rapport de reunion hebdomadaire pour un projet it, contenu : taches realisees, priorites de la semaine, problemes techniques.",
    "compte rendu de reunion avec le client sur la validation des specifications, discussions : points bloques, modifications apportees, nouvelles dates.",
    "resume de reunion sur la strategie de developpement international, sujets : analyse des marches, priorisation, ressources necessaires.",

    #analyse de risque
    "analyse des risques pour un projet de migration it, contenu : evaluation des failles de securite, risques de perte de donnees, plan de mitigation.",
    "document d'analyse de risques pour une campagne marketing digitale, points : reputation en ligne, violations rgpd, impact budgetaire.",
    "rapport d'analyse des risques financiers pour un projet d'expansion, inclut : fluctuations des taux de change, evolution de la demande, contraintes reglementaires.",
    "evaluation des risques pour une implantation internationale, sections : risques culturels, compliance locale, conflits politiques.",
    "analyse de risques cybersecurite pour un systeme cloud, contenu : protection contre les attaques ddos, gestion des identites, sauvegardes.",
    "document de gestion des risques pour un chantier de construction, details : accidents de travail, delais de livraison, variations climatiques.",
    "rapport d'evaluation des risques operationnels pour un site de production, sujets : pannes d'equipement, manque de personnel, gestion des stocks.",
    "analyse des risques pour une acquisition d'entreprise, contenu : dettes cachees, integration des systemes, retention des talents.",
    "document d'evaluation des risques pour un evenement public, inclut : securite des participants, risque meteorologique, logistique.",
    "rapport d'analyse de risques pour un investissement en bourse, sections : volatilite du marche, evolution economique, tendances sectorielles.",
    "document d'evaluation des risques environnementaux pour un projet industriel, contenu : pollution, gestion des dechets, respect des normes.",
    "analyse des risques pour un projet agile, themes : priorisation incorrecte, dependances externes, resistance au changement.",
    "rapport de gestion des risques pour un projet logiciel, inclut : bugs critiques, depassements de budget, complexite des integrations.",
    "evaluation des risques pour une chaine d'approvisionnement, contenu : retard des livraisons, hausse des couts des matieres premieres, ruptures de stock.",
    "document d'analyse des risques pour un projet de recherche scientifique, details : risques technologiques, contraintes budgetaires, retards administratifs.",
    "rapport d'evaluation des risques pour une campagne publicitaire, inclut : mauvaise reception par le public, erreurs de ciblage, depassement de budget.",
    "analyse des risques pour un projet de renovation, themes : augmentation des couts, delais prolongees, litiges contractuels.",
    "document d'analyse des risques pour un partenariat strategique, inclut : desaccords sur les objectifs, perte de controle, incompatibilite des cultures d'entreprise.",
    "evaluation des risques de sante et securite pour un entrepot, contenu : incendies, accidents lies au transport de marchandises, ergonomie des postes.",
    "rapport d'analyse des risques pour un projet de transformation digitale, themes : resistance des employes, problemes de compatibilite, surcharge des equipes.",

    #emails
    "hello, je t'ecris pour confirmer la reception des documents contractuels que vous avez transmis. si vous avez des questions ou remarques, n'hesitez pas a me le faire savoir. je reste disponible pour toute clarification. cordialement, jean dubois",
    "hello, je souhaiterais organiser une reunion pour discuter des prochaines etapes de notre collaboration. je propose les dates suivantes : 10 fevrier, 12 fevrier ou 15 fevrier. merci de me confirmer celle qui te convient ou de proposer une autre disponibilite. au plaisir d'echanger, cordialement, sophie martin",
    "bonjour, je vous partage en piece jointe les resultats de l'analyse effectuee sur vos donnees. les points cles sont resumes dans le document joint. je reste disponible pour discuter des resultats et des prochaines etapes. bien a vous, julien leroy",
    "bonjour, nous avons constate un retard dans le reglement de votre derniere facture, d'un montant de 4500 euros. nous vous invitons a effectuer ce paiement avant le 28 janvier pour eviter toute penalite. merci de nous informer si vous rencontrez des difficultes. cordialement, nathalie bernard",
    "bonjour a tous, nous souhaitons vous informer d'un changement concernant notre politique interne sur les horaires flexibles. celui-ci prendra effet a partir du 1er mars. nous vous remercions de votre collaboration pour une transition fluide. si vous avez des questions, n'hesitez pas a me contacter. bien cordialement, marie dubois",
    "bonjour, nous avons le plaisir de vous inviter a une formation en ligne sur la securite des donnees, qui aura lieu le 3 fevrier a 14h. vous trouverez le lien d'inscription ici : www.inscription-formation.fr. nous esperons vous y voir nombreux. cordialement, thomas durand",
    "bonjour, nous confirmons notre commande pour les produits suivants : 20 claviers ergonomiques et 30 souris sans fil. merci de nous transmettre une confirmation ainsi qu'une estimation de la date de livraison. cordialement, aline roche",
    "salut, je te partage une mise a jour concernant l'avancement du projet digital horizon. voici les principales etapes realisees : configuration des serveurs, creation des comptes utilisateurs et tests preliminaires. les prochaines etapes incluent le deploiement global. n'hesitez pas a me faire part de vos retours. bien cordialement, laurent grimaldi",
    "bonjour, merci pour le temps que vous nous avez accorde lors de notre derniere rencontre. je vous joins une proposition detaillee qui resume les points abordes. je reste disponible pour toute question ou precision. cordialement, clara fernandez",
    "bonjour, veuillez trouver ci-joint la version finale de notre proposition commerciale. nous attendons votre validation avant le 5 fevrier pour pouvoir avancer. si vous avez des remarques, je suis a votre disposition. cordialement, pierre rodriguez",
    "bonjour, nous rencontrons un probleme technique sur la synchronisation des donnees entre les serveurs. l'impact actuel est un ralentissement des acces pour les utilisateurs. pourriez-vous intervenir rapidement ? merci d'avance pour votre retour. cordialement, emilie chavigny",
    "bonjour, je vous rappelle notre entretien annuel d'evaluation prevu pour le 10 fevrier a 15h. pensez a preparer les documents suivants : votre auto-evaluation et le rapport d'activite trimestriel. si vous avez besoin d'ajuster l'horaire, faites-le moi savoir. cordialement, michel renault",
    "bonjour, je vous partage le compte rendu de notre reunion du 18 janvier. vous trouverez les decisions prises ainsi que les actions a suivre. merci de verifier si tous les points sont corrects. bien a vous, sophie masson",
    "bonjour, nous sommes ravis de vous annoncer le lancement de notre nouveau produit, le power cleaner pro. il sera disponible des le 20 fevrier. vous pouvez consulter les details ici : www.power-cleaner.fr. cordialement, lucie malot",
    "bonjour, nous souhaiterions obtenir un devis pour la conception d'une application mobile. pourriez-vous nous fournir une estimation de cout et de delai ? merci de votre retour rapide. bien cordialement, leo fontaine",
    "bonjour a tous, je vous partage les resultats trimestriels de notre activite. voici les chiffres cles : chiffre d'affaires en hausse de 12 %, augmentation de la satisfaction client et reduction des couts fixes. merci a chacun pour votre engagement. continuons sur cette dynamique. bien cordialement, yann dupont",
    "bonjour, nous aimerions vous inviter a rejoindre le projet neo. votre role consistera a coordonner les equipes et assurer le suivi des livrables. merci de confirmer votre participation avant le 30 janvier. bien cordialement, claire perrin",
    "bonjour, nous souhaitons vous informer qu'un arret temporaire de service est prevu le 1er fevrier, de 22h a 4h, pour maintenance. merci de votre comprehension. cordialement, marion laporte",
    "bonjour, pourriez-vous nous fournir des informations complementaires sur les caracteristiques techniques du materiel propose ? nous avons besoin de clarifications sur la compatibilite avec notre infrastructure existante. merci pour votre retour rapide. cordialement, paul roux",
    "bonjour a tous, nous avons le plaisir d'accueillir camille lemieux dans notre equipe. elle occupera le poste de responsable marketing digital a partir du 15 fevrier. merci de lui reserver un accueil chaleureux. cordialement, maxime durieux",

    #lettres de motivation
    "je souhaite postuler au poste de chef de projet au sein de votre entreprise, motive par ma passion pour la gestion de projets innovants",
    "diplomé en finance, je suis interesse par l'offre d'analyste financier et je pense pouvoir contribuer a vos objectifs strategiques",
    "dans le cadre de mon projet professionnel, je suis motive a integrer votre equipe en tant que commercial",
    "ayant acquis une solide experience en marketing digital, je souhaite rejoindre votre entreprise pour relever de nouveaux defis",
    "convaincu par vos valeurs et votre mission, je souhaite contribuer a votre croissance en tant qu'assistant administratif",
    "apres avoir obtenu un diplome en ingenierie, je suis enthousiaste a l'idee de collaborer avec votre equipe de developpement",
    "je suis persuade que mes competences en communication et en gestion de projet repondent parfaitement aux attentes de votre poste",
    "mes experiences precedentes m'ont permis de developper une rigueur et une organisation que je souhaite mettre a profit chez vous",
    "je suis tres interesse par le secteur des energies renouvelables et souhaite integrer votre entreprise comme ingenieur energetique",
    "passionne par la relation client, je suis convaincu que mon dynamisme et mon sens de l'organisation sont des atouts",
    "suite a votre offre d'emploi, je souhaite mettre mes competences en gestion des operations logistiques au service de votre entreprise",
    "lettre de motivation pour un poste de responsable marketing, madame, monsieur, je suis convaincu que mes 5 ans d’experience dans le domaine du marketing strategique, combines a mon diplome de master en marketing digital, me permettront de contribuer au succes de votre entreprise.",
    "lettre de motivation pour un poste de secretaire administrative, madame, monsieur, ayant un excellent sens de l’organisation et de communication, je souhaiterais mettre mes competences au service de votre equipe, comme en temoigne mon experience dans un environnement similaire.",
    "lettre de motivation pour un poste de comptable junior, madame, monsieur, passionne par les chiffres et ayant recemment obtenu mon bts comptabilite, je suis motive a rejoindre votre entreprise pour y apporter mes competences en gestion financiere et en analyse de donnees.",
    "lettre de motivation pour un poste de developpeur web, madame, monsieur, titulaire d’une licence en informatique, j’ai acquis de solides competences en programmation et developpement web. je souhaite rejoindre votre equipe dynamique pour contribuer au succes de vos projets digitaux.",
    "lettre de motivation pour un poste de chef de projet, madame, monsieur, avec 6 ans d'experience en gestion de projets complexes, je suis convaincu que ma capacite a coordonner des equipes et a gerer les budgets serait un atout pour votre entreprise.",
    "lettre de motivation pour un poste de designer graphique, madame, monsieur, passionnee par la creation visuelle et avec une expertise en design numerique, je desire integrer votre entreprise pour apporter ma creativite et mon sens du detail au service de vos projets.",
    "lettre de motivation pour un poste de responsable des ressources humaines, madame, monsieur, forte de mon experience de 5 ans dans le domaine des ressources humaines, je serais ravie de contribuer a la gestion du capital humain au sein de votre societe.",
    "lettre de motivation pour un poste de vendeur en boutique, madame, monsieur, grace a mes experiences de vente et mon excellent sens du service client, je souhaite rejoindre votre equipe et contribuer au developpement de vos ventes.",
    "lettre de motivation pour un poste de chef de produit, madame, monsieur, avec une formation en marketing et plusieurs annees d’experience dans la gestion de produits, je suis enthousiaste a l'idee de rejoindre votre equipe pour piloter la strategie de vos produits."
]

labels = [
    "facture", 
    "facture",
    "facture",
    "facture", 
    "facture",
    "facture", 
    "facture",
    "facture",
    "facture", 
    "facture",
    "facture",
    "facture", 
    "facture",
    "facture",
    "facture", 
    "facture",
    "facture", 
    "facture",
    "facture",
    "facture", 
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "devis",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "contrat",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande",
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "bon_de_commande", 
    "bon_de_commande",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "fiche_de_paie", 
    "fiche_de_paie",
    "fiche_de_paie",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "article_de_presse", 
    "article_de_presse", 
    "article_de_presse",
    "recherche", 
    "recherche", 
    "recherche",
    "recherche", 
    "recherche", 
    "recherche", 
    "recherche", 
    "recherche",
    "recherche", 
    "recherche",
    "recherche",
    "recherche", 
    "recherche", 
    "recherche",
    "recherche", 
    "recherche", 
    "recherche", 
    "recherche", 
    "recherche",
    "recherche",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
    "procedure",
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
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "referentiel",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "attestation",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "cv",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "bon_de_livraison",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "cahier_des_charges",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "document_darchitecture_technique",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "compte-rendu_de_reunion",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "analyse_de_risque",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "email",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation",
    "lettre_de_motivation"
]


# DATA_FILE = 'models/data.json'
DATA_PATH = os.path.join(get_base_app_files_path(), 'models', 'data.json')

text = []
label = []

def charger_donnees():
    """Load existing texts and labels from the data file.

    If the data file does not exist, initializes empty lists.

    :return: None
    """
    global text, label
    print("data path", DATA_PATH)
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = data["textes"]
        label = data["labels"]
    else:
        text = []
        label = []

def sauvegarder_donnees(textes, labels):
    """Save texts and labels to the data file.

    :param list textes: List of texts to save
    :param list labels: Corresponding list of labels
    :return: None
    """
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump({"textes": textes, "labels": labels}, f)

def ajouter_texte_avec_type(path, type_texte):
    """Analyze a file, preprocess it, and add it to the dataset with a label.

    If a text with the same label exists, it will be replaced to maintain balance.

    :param str path: Path to the file to analyze
    :param str type_texte: Type/category of the text
    :return: None
    """
    charger_donnees()

    #analyse et pré-traitement
    nouveau_texte = analyse_fichier(path)

    if nouveau_texte.strip():
        # suppression d'un des autres exemples du même label pour l'équilibre
        if type_texte in labels:
            index = labels.index(type_texte)
            del textes[index]
            del labels[index]

        # Ajout du nouveau texte et label
        text.append(nouveau_texte)
        label.append(type_texte)

        entrainer_modele(text,label)

        # Sauvegarder les nouvelles données
        sauvegarder_donnees(text, label)

        print("fichier a ete ajouter mon exemple a la categorie : ",label)

    else :
        print("ERREUR - le fichier n'a pas pu etre ajouter comme exemple")

def reinitialiser_donnees():
    """Reset the dataset and retrain the model.

    :return: None
    """
    sauvegarder_donnees(textes, labels)
    entrainer_modele(textes, labels)

def entrainer_modele(textes, labels):
    """Train a machine learning model to classify text types.

    This function preprocesses texts, applies TF-IDF vectorization, trains an SVM model,
    and optimizes it using GridSearchCV. The trained model is saved for future use.

    :param list textes: List of preprocessed texts
    :param list labels: Corresponding labels for classification
    :return: None
    """
    # Télécharger les stopwords de NLTK
    try:
        stopwords_fr = stopwords.words('french')
    except LookupError:
        nltk.download('stopwords')
        stopwords_fr = stopwords.words('french')

    # Ajout de stopwords
    stopwords_plus = ['d', 'l', 'avoir', 'etre', 'mettre', 'c', 's', 'a', 'b', 'e', 'f', 'g', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    stopwords_final = stopwords_fr + stopwords_plus

    textes_pretraites = [preprocess_text(t) for t in textes]

    vectorizer = TfidfVectorizer(stop_words=stopwords_final, ngram_range=(1, 2))

    X = vectorizer.fit_transform(textes_pretraites)
    classifier = SVC(class_weight='balanced', kernel='linear')
    classifier.fit(X, labels)

    #Validation croisée
    # Définir les paramètres à tester pour le SVM avec GridSearchCV
    parameters = {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf'], 'gamma': ['scale', 'auto']}

    # Appliquer la recherche sur grille
    grid_search = GridSearchCV(SVC(class_weight='balanced'), parameters, cv=3)
    grid_search.fit(X, labels)

    # Afficher les meilleurs paramètres et le meilleur score
    print(f"Meilleurs paramètres: {grid_search.best_params_}")
    print(f"Meilleur score: {grid_search.best_score_}")

    # Entraînement avec les meilleurs paramètres trouvés par GridSearchCV
    best_classifier = grid_search.best_estimator_

    scores = cross_val_score(best_classifier, X, labels, cv=4)
    print(f"Validation croisee : {scores.mean():.3f} ± {scores.std():.3f}")

    base_path = get_base_app_files_path()
    models_path = os.path.join(base_path, 'models')
    os.makedirs(models_path, exist_ok=True)

    # Sauvegarder les fichiers de modele dans le répertoire models
    joblib.dump(classifier, os.path.join(models_path, "model_svm.joblib"))
    joblib.dump(vectorizer, os.path.join(models_path, "vectorizer_tfidf.joblib"))


if __name__ == "__main__":
    print("Training...")
    charger_donnees()
    entrainer_modele(textes,labels)
    print("...Completed")
