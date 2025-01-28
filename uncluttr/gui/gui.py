""" This module contains the GUI of the application. """

import configparser
import multiprocessing
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from uncluttr.file_treatement.file_treatement import file_analysis
from uncluttr.file_treatement.training_models import entrainer_modele
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.core.configuration import update_daemon_path,update_storage_directory


# Lecture du fichier de configuration
config = configparser.ConfigParser()
base_path = get_base_app_files_path()
config_path = os.path.join(base_path, 'configuration', 'conf.ini')
config.read(config_path)
path_dameon_directory = config['settings']['directory_to_watch']
path_storage = config['settings']['storage_path']
root = TkinterDnD.Tk()
path_accept = None
daemon_process = None 
path_space = None

class DirectoryTreeViewer:
    def __init__(self, root):
        self.root = root
        
        self.current_directory = tk.Label(root, text="Dossier de stockage actuel: ",bg='#2f2f2f', fg='white')
        self.current_directory.pack(padx=10, anchor='w')
        self.path_space_storage = tk.Text(root, height=1, width=75)
        self.path_space_storage.insert(tk.INSERT,path_storage)
        self.path_space_storage.pack(pady=10, padx=10, anchor='w')
        
        self.select_button = tk.Button(self.root, text="Changer le dossier de stockage", command=self.change_directory)
        self.select_button.pack(padx=10)

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(expand=True, fill=tk.BOTH,padx=20)

        self.tree.heading("#0", text="Structure de votre dossier: ", anchor=tk.W)

    def change_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            update_storage_directory(directory)
            global path_storage
            path_storage = directory
            self.path_space_storage.delete("1.0", tk.END)
            self.path_space_storage.insert(tk.INSERT,directory)
            self.display_directory_tree(directory)

    def display_directory_tree(self, directory):
        self.tree.delete(*self.tree.get_children())
        self.add_node(directory, "")

    def add_node(self, path, parent):
        node = self.tree.insert(parent, 'end', text=os.path.basename(path), open=False)
        if os.path.isdir(path):
            try:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    self.add_node(full_path, node)
            except PermissionError:
                messagebox.showerror("Permission Error", f"Permission denied for directory: {path}")
    
def init_page():
    
    for widget in root.winfo_children():
        widget.destroy()
    root.title("Uncluttr")
    root.geometry("800x600")
    root.configure(bg='#2f2f2f')
    root.resizable(False, False)
    
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Pages", menu=file_menu)
    file_menu.add_command(label="Page Principale", command=home_page)
    file_menu.add_command(label="Mon Arborescence", command=arborescence_page)
    file_menu.add_command(label="Parametrage", command=add_file_page)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About")
    help_menu.add_command(label="Exit", command=root.quit)
    
    # Texte "Uncluttr" + ligne horizontale 
    uncluttr_label = tk.Label(root, text="Uncluttr", font=("Helvetica", 20, "bold"), bg='#2f2f2f', fg='white')
    separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN, bg='#2f2f2f')
    
    # Placement des éléments
    uncluttr_label.pack(pady=10)
    separator.pack(fill=tk.X, pady=10, anchor='w')
    

        
def start_gui(process: multiprocessing.Process=None):
    """Start the GUI."""
    global daemon_process
    if process is not None:
        daemon_process = process
    home_page()
        
    
def home_page():
    global path_accept, path_storage, path_space
    init_page()

    # Espace pour path
    path_label = tk.Label(root, text="Nous surveillons ce dossier :", bg='#2f2f2f', fg='white')
    path_space = tk.Text(root, height=1, width=50, bg='lightgrey')
    path_space.insert(tk.INSERT,path_dameon_directory)

    # Bouton pour selectionner un dossier
    select_directory_button = tk.Button(root, text="Choisir un dossier", command=select_directory)

    # Bouton pour le changement de path
    path_accept = tk.Button(root, text="Voulez-vous changer le path pour le daemon ?",command=sauvegarde_du_path)

    if daemon_process is not None:
        path_accept = tk.Button(root, text="Valider le changement de chemin?",
                                command=lambda: sauvegarde_du_path(daemon_process))
    else:
        path_accept = tk.Button(root, text="Impossible d'interagir avec le daemon",
                                state=tk.DISABLED)

    # Texte en gras "Ajout de fichiers"
    ajout_fichiers_label = tk.Label(root, text="Ajout de fichiers", font=("Helvetica", 12, "bold"), bg='#2f2f2f', fg='white')

    # Bouton pour ouvrir un fichier
    button_open = tk.Button(root, text="Ouvrir un fichier", command=open_file)

    # Zone de drag-and-drop
    drop_area = tk.Label(root, text="Glisser / Déposer", bg="white", width=90, height=10)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop_file)

    # Ajout des éléments à la fenêtre
    path_label.pack(pady=5, padx=10, anchor='w')
    path_space.pack(pady=5, padx=10, anchor='w')
    select_directory_button.pack(pady=5, padx=10, anchor='w')
    path_accept.pack(pady=5, padx=10, anchor='e')
    ajout_fichiers_label.pack(pady=(40, 10))
    button_open.pack(pady=5)
    drop_area.pack(pady=10)
    
    # Lancement de l'application
    root.mainloop()

def select_directory():
        """Open a file explorer and return the selected path."""
        chosen_path = filedialog.askdirectory()
        if chosen_path:
            path_space.delete("1.0", tk.END)
            path_space.insert(tk.INSERT, chosen_path)

def sauvegarde_du_path(gui_daemon_process: multiprocessing.Process):
    """Save the new path."""
    
    new_path = path_space.get("1.0", tk.END).strip()
    gui_daemon_process = update_daemon_path(new_path, gui_daemon_process)

    # Redéfinir le bouton pour utiliser le nouveau processus
    path_accept.config(text="Voulez-vous changer le path à nouveau ?",
                        command=lambda: sauvegarde_du_path(gui_daemon_process))
    
    # Mettre à jour le path affiché
    path_space.delete("1.0", tk.END)
    path_space.insert("1.0", new_path)
    global path_dameon_directory
    path_dameon_directory = new_path

def open_file():
    """Ouvre un fichier via un explorateur et affiche son contenu."""
    try:
        file_path = filedialog.askopenfilename(
            # filetypes=[("PDF files", "*.pdf"), ("ZIP files", "*.zip"), ("Image files", "*.jpg;*.jpeg;*.png")]
            filetypes=[("Handled file types", "*.pdf;*.zip;*.jpg;*.jpeg;*.png")]
            )
        if file_path:
            file_analysis(file_path)

    except Exception as e:
        print(f"An interanl error occurred : {e}")
        tk.messagebox.showerror("Erreur", f"Une erreur interne imprévue est survenue : {e}")
        
def drop_file(event):
    """Récupère le fichier déposé dans la zone de drag-and-drop."""
    try:
        file_path = event.data.replace('{', '').replace('}', '')
        file_type = file_path.split('.')[-1]
        if file_type == "zip" or file_type == "pdf" or file_type == "jpg" or file_type == "jpeg" or file_type == "png":
            file_analysis(file_path)
        else:
            tk.messagebox.showerror("Erreur", "Seuls les fichiers ZIP, PDF, Jpeg et PNG sont acceptés.")
    except Exception as e:
        tk.messagebox.showerror("Erreur", f"Une erreur interne imprévue est survenue : {e}")
        
        
def arborescence_page():
    """Page pour afficher l'arborescence des fichiers."""
    init_page()
    parametrage_label = tk.Label(root, text="Mon Arborescence", font=("Helvetica", 16, "bold"), bg='#2f2f2f', fg='white')
    parametrage_label.pack(pady=(20, 10), anchor='w')
    separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN, bg='#2f2f2f', width=400)
    separator.pack(pady=10, anchor='w')
    
    app=DirectoryTreeViewer(root)
    app.display_directory_tree(path_storage)
    footer_frame = tk.Frame(root, bg='#2f2f2f')
    footer_frame.pack(side=tk.BOTTOM, pady=10)

    back_button = tk.Button(footer_frame, text="Retour", command=home_page)
    back_button.pack(side=tk.LEFT, padx=10)
    

def add_file_page():
    """Page pour ajouter un fichier d'apprentissage."""
    init_page()
    # Options Menu Déroulant
    options = [
        "Facture", 
        "Devis",
        "Contrat",
        "Bon de commande", 
        "Fiche de paie", 
        "Article de presse", 
        "Recherche", 
        "Référentiel",
    ]
    
    parametrage_label = tk.Label(root, text="Paramétrage de l'IA", font=("Helvetica", 16, "bold"), bg='#2f2f2f', fg='white')
    parametrage_label.pack(pady=(20, 10), anchor='w')
    separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN, bg='#2f2f2f', width=400)
    separator.pack(pady=10, anchor='w')
    
    content_frame = tk.Frame(root, bg='#2f2f2f')
    content_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True, anchor='w')
    
    dropdown_label = tk.Label(content_frame, text="Choisir un fichier exemple :", bg='#2f2f2f', fg='white', anchor='w', font=("Helvetica", 12))
    parametrage_label.pack(pady=(20, 10), anchor='w')
    
    file_path_label = tk.Label(content_frame, text="Aucun fichier sélectionné", bg='#2f2f2f', fg='white', anchor='w')
    file_path_label.pack(fill=tk.X, pady=5, anchor='w')
    
    select_file_button = tk.Button(content_frame, text="Sélectionner un fichier", command=lambda: file_path_label.config(text=filedialog.askopenfilename()))
    select_file_button.pack(pady=5, anchor='w')
    
    # Menu déroulant
    dropdown_label = tk.Label(content_frame, text="Sélectionnez une catégorie de fichier :", bg='#2f2f2f', fg='white', anchor='w', font=("Helvetica", 12))
    dropdown_label.pack(pady=(20, 5), anchor='w')
    
    selected_option = tk.StringVar(root)
    selected_option.set(options[0])
    
    dropdown_menu = ttk.Combobox(content_frame, textvariable=selected_option, values=options, state="readonly")
    dropdown_menu.pack(pady=5, padx=10, anchor='w')
    # Bouton pour valider la sélection
    validate_button = tk.Button(content_frame, text="Valider la sélection", command=lambda: learning(selected_option.get(), file_path_label.cget("text")))
    validate_button.pack(pady=30, anchor='w')
    # Lancement de l'application
    root.mainloop()
 
def learning(type_file, file_path):
    """Exemple de fonction pour Eva"""


if __name__ == "__main__":
    print("Starting GUI...")
    start_gui()