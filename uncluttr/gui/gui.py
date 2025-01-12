import configparser, sys, os, shutil
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

import shutil

import fitz  # PyMuPDF

from uncluttr.fileTreatement.fileTreatement import folderAnalysis
from uncluttr.daemon.daemon import start_daemon
config = configparser.ConfigParser()
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.getcwd()

config_path = os.path.join(base_path, 'configuration', 'conf.ini')
config.read(config_path)
path = config['settings']['directory_to_watch']
root = TkinterDnD.Tk()
path_space = tk.Text(root, height=1, width=50)

def start_gui():
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
    config['settings']['directory_to_watch'] = path_space.get("1.0",tk.END).split("\n")[0]
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    start_daemon()
    
def open_file():
    
    """Ouvre un fichier via un explorateur et affiche son contenu."""
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("ZIP files", "*.zip")]
        )    
    if file_path:
        shutil.copy(file_path, path_space.get("1.0",tk.END).split("\n")[0] )
        folderAnalysis( path_space.get("1.0",tk.END).split("\n")[0])
        
        

def drop_file(event):
    """Récupère le fichier déposé dans la zone de drag-and-drop."""
    file_path = event.data
    file_type = file_path.split('.')[-1]
    if file_type == "zip" or file_type == "pdf":
        shutil.copy(file_path, path)
        folderAnalysis()  
    else:
        tk.messagebox.showerror("Erreur", "Seuls les fichiers ZIP et PDF sont acceptés.")



if __name__ == "__main__":
    print("Starting GUI...")
    start_gui()