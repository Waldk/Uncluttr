""" This module contains the GUI of the application. """

import configparser
import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
# Vous avez vraiment besoin de cet import ? vous l'utilisez nulle part de ce que je vois
# import fitz  # PyMuPDF
from uncluttr.file_treatement.file_treatement import file_analysis
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.core.configuration import update_daemon_path


# Lecture du fichier de configuration
config = configparser.ConfigParser()

base_path = get_base_app_files_path()
config_path = os.path.join(base_path, 'configuration', 'conf.ini')
config.read(config_path)
path = config['settings']['directory_to_watch']
root = TkinterDnD.Tk()
path_space = tk.Text(root, height=1, width=50)

DAEMON_PROCESS = None

def start_gui():
    """Start the GUI."""
    # Fenêtre principale
    root.title("Uncluttr")
    root.geometry("800x600")

    # Espace pour path
    path_label = tk.Label(root, text="Le path actuel est :")
    path_space.insert(tk.INSERT,path)
    # Bouton pour le changement de path
    path_accept = tk.Button(root, text="Voulez-vous changer le path ?",command=sauvegarde_du_path)

    #Placement
    path_label.pack(pady=5)
    path_space.pack(pady=5)
    path_accept.pack(pady=5)

    # Bouton pour ouvrir un fichier
    button_open = tk.Button(root, text="Ouvrir un fichier", command=open_file)
    button_open.pack(pady=5)

    # Zone de drag-and-drop
    drop_area = tk.Label(root, text="Déposez un fichier ici", bg="lightgrey", width=70, height=4)
    drop_area.pack(pady=10)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop_file)

    # Lancement de l'application
    root.mainloop()

def sauvegarde_du_path():
    """Save the new path."""
    global DAEMON_PROCESS
    new_path = path_space.get("1.0", tk.END).strip()
    print(new_path)
    DAEMON_PROCESS = update_daemon_path(new_path, DAEMON_PROCESS)


    # Crée des processus en plus, c'est pas ce que l'on veut et on ne peut pas les arreter depuis l'ide, bonjour les fuites mémoires

    # config['settings']['directory_to_watch'] = path_space.get("1.0",tk.END).split("\n")[0]
    # with open(config_path, 'w', encoding='utf-8') as configfile:
    #     config.write(configfile)
    # start_daemon()


def open_file():
    """Ouvre un fichier via un explorateur et affiche son contenu."""
    try:
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("ZIP files", "*.zip")]
            )
        if file_path:
            file_analysis(file_path)

            # on doit pas analyser tout le folder à chaque fois que l'on veut trier un fichier
            # copier le ficher dans le direcorty_to_watch
            # fais qu'il sera aussi scanné par le daemon ce qui est pas ce qu'on veut
            # et on scanne pas tout le dossier le daemon regarde deja tous les subfolders
            # dites si vous trouvez ça pas cohérent

            # shutil.copy(file_path, path_space.get("1.0",tk.END).split("\n")[0] )
            # folder_analysis( path_space.get("1.0",tk.END).split("\n")[0])
    except Exception as e:
        tk.messagebox.showerror("Erreur", f"Une erreur interne imprévue est survenue : {e}")


def drop_file(event):
    """Récupère le fichier déposé dans la zone de drag-and-drop."""
    try:
        file_path = event.data.replace('{', '').replace('}', '')
        file_type = file_path.split('.')[-1]
        if file_type == "zip" or file_type == "pdf":
            file_analysis(file_path)

            # on doit pas analyser tout le folder à chaque fois que l'on veut trier un fichier
            # copier le ficher dans le direcorty_to_watch
            # fais qu'il sera aussi scanné par le daemon ce qui est pas ce qu'on veut
            # et on scanne pas tout le dossier le daemon regarde deja tous les subfolders
            # dites si vous trouvez ça pas cohérent

            # shutil.copy(file_path, path)
            # folder_analysis()
        else:
            tk.messagebox.showerror("Erreur", "Seuls les fichiers ZIP et PDF sont acceptés.")
    except Exception as e:
        tk.messagebox.showerror("Erreur", f"Une erreur interne imprévue est survenue : {e}")


if __name__ == "__main__":
    print("Starting GUI...")
    start_gui()
