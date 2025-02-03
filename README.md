# Uncluttr

Notre projet vise à faciliter la numérisation et l’archivage intelligent des documents d’une entreprise grâce à un système automatisé de traitement et de tri. Les fichiers ajoutés sont analysés puis classés dynamiquement selon une arborescence évolutive, qui s’adapte à l’arrivée de nouveaux documents.
L’utilisateur définit un dossier surveillé, où chaque fichier ajouté est immédiatement traité selon plusieurs critères : date, type de document et thème principal. L’application fonctionne en local, garantissant ainsi la confidentialité des données.
L’interface graphique permet de visualiser et ajuster le classement avant validation. Après traitement, l’utilisateur reçoit des suggestions d’organisation et peut naviguer entre elles avant de confirmer le classement définitif. Il permet aussi l’ajout d’exemples pour les critères de tri du document pour améliorer la classification des documents de l’entreprise mais également choisir l’ordre de rangement dans l’arborescence.

Notre solution utilise Watchdog, un démon de surveillance open-source, pour détecter en temps réel l’ajout de nouveaux fichiers dans le dossier sélectionné. L’analyse documentaire repose sur un algorithme de classification automatique, prenant en compte les métadonnées et le contenu. Pour les PDF non structurés et les images, nous intégrons un moteur OCR permettant d’extraire et d’analyser le texte. Une base de données locale assure la gestion des métadonnées et une recherche rapide des fichiers archivés. L’interface est développée en Python avec Tkinter/PyQt, et l’automatisation du traitement est gérée via des scripts Python.


### Fonctionnement de l'application
- Vérifier que poetry, est bien installé, si ce n'est pas le cas, faites la commande ```pip install poetry```, poetry étant un manager de package sur python

- Créer et activer votre venv avec
    - dans un terminal de préférence un bash
    - ```python -m venv .venv``` ou ```python -m venv```
    - ```source .venv/Scripts/activate```
    - normalement vous devriez voir un (.venv) dans votre terminal au dessus de la ligne où vous allez éxecuter vos futurs commandes 
![alt text](assets/readme/image.png)

- Lancer la commande ```poetry install```
- Lancer l'application à l'aide de la commande ```[to define]```, (pour l'instant: ```python -m uncluttr.core.main```)  ou :
    - ```python uncluttr/daemon/daemon.py``` si vous testez uniquement le daemon
    - ```python uncluttr/gui/gui.py``` si vous testez uniquement l'interface graphique
    - etc
- pour l'arrêter, faire un ```CTRL+c``` dans le terminal où vous avez lancé l'application

- Installer un linter d'ailleurs si possible histoire de faire du code qui suit les conventions, genre l'extension ```Pylint``` sur vscode
- Et pensez à gérer vos exceptions, histoire d'éviter que ça crash


### Releases

- Dans la section **Releases** de github, vous pouvez retrouver le dernier ```.exe``` fonctionnel de l'application.
- Pour build un ```.exe```, lancer la commande ```pyinstaller --onefile --name Uncluttr --add-data "configuration/conf.ini;configuration" --add-data "configuration/document_keywords.json;configuration" --add-data "models/model_svm.joblib;models" --add-data "models/vectorizer_tfidf.joblib;models" --additional-hooks-dir=./uncluttr uncluttr/core/main.py```, vous retrouverez le ```.exe``` dans le dossier dist.
    - Si vous avez déjà build une fois, vous devriez avoir un fichier ```.spec```, auquel cas vous pouvez build avec ```pyinstaller Uncluttr.spec```

### Documentation

Vous pouvez consulter la documentation complète sur [Read the Docs](https://waldk.github.io/Uncluttr/index.html#).
