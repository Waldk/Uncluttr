import configparser
import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
import fitz  # PyMuPDF
from uncluttr.fileTreatement.fileTreatement import fileAnalysis
import shutil

from uncluttr.fileTreatement.fileTreatement import folderAnalysis

config = configparser.ConfigParser()
config.read('configuration/conf.ini')
path = config['settings']['directory_to_watch']

def open_file():
    
    """Ouvre un fichier via un explorateur et affiche son contenu."""
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("ZIP files", "*.zip")]
        )    
    if file_path:
        shutil.copy(file_path, path)
        folderAnalysis()
        
        

def drop_file(event):
    """Récupère le fichier déposé dans la zone de drag-and-drop."""
    file_path = event.data
    file_type = file_path.split('.')[-1]
    if file_type == "zip" or file_type == "pdf":
        shutil.copy(file_path, path)
        folderAnalysis()  
    else:
        tk.messagebox.showerror("Erreur", "Seuls les fichiers ZIP et PDF sont acceptés.")

def start_gui():
    # Fenêtre principale
    root = TkinterDnD.Tk()
    root.title("Uncluttr")
    root.geometry("800x600")

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

if __name__ == "__main__":
    print("Starting GUI...")
    start_gui()