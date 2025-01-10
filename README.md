# Uncluttr

- Vérifier que poetry, est bien installé, auquel cas, faites la commande ```pip install poetry```, poetry étant un manager de package sur python

- Créer et activer votre venv avec
    - dans un terminal de préférence à un bash
    - ```python -m venv```
    - ```. source .venv/Scripts/activate```
    - normalement bous devriez voir un (.venv) dans votre terminal au dessus de la ligne où vous allez écecuter vos futurs commandes 
    - ![alt text](assets/readme/image.png)

- Lancer la commande "poetry --install"
- Lancer l'application à l'aide de la commande ```[to define]```, (pour l'instant: ```python -m uncluttr.core.main```)  ou :
    - ```python uncluttr/daemon/daemon.py``` si vous testez uniquement le daemon
    - ```python uncluttr/gui/gui.py``` si vous testez uniquement l'interface graphique'