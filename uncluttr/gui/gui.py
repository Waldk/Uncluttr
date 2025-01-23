""" This module contains the GUI of the application. """

import configparser
import multiprocessing
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from uncluttr.file_treatement.file_treatement import file_analysis
from uncluttr.file_treatement.training_models import entrainer_modele
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
path_accept = None

class DirectoryTreeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Directory Tree Viewer")

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.select_button = tk.Button(self.frame, text="Select Directory", command=self.select_directory)
        self.select_button.pack(side=tk.LEFT, padx=10)

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.heading("#0", text="Directory Structure", anchor=tk.W)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
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


def start_gui(daemon_process: multiprocessing.Process=None):
    """Start the GUI."""
    # entrainer_modele()

    # Barre de tache en header
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Action", menu=file_menu)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Arborecence", command=second_page)

    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About")

    # Fenêtre principale
    root.title("Uncluttr")
    root.geometry("800x600")
    global path_accept

    # Espace pour path
    path_label = tk.Label(root, text="Le path actuel pour le daemon est :")
    path_space.insert(tk.INSERT,path)

    # Bouton pour le changement de path
    path_accept = tk.Button(root, text="Voulez-vous changer le path pour le daemon ?",command=sauvegarde_du_path)
    

    if daemon_process is not None:
        path_accept = tk.Button(root, text="Voulez-vous changer le path ?",
                                command=lambda: sauvegarde_du_path(daemon_process))
    else:
        path_accept = tk.Button(root, text="Impossible d'interagir avec le daemon",
                                 state=tk.DISABLED)

    #Placement
    path_label.pack(pady=5)
    path_space.pack(pady=5)
    path_accept.pack(pady=5)

    # Bouton pour ouvrir un fichier
    button_open = tk.Button(root, text="Ouvrir un fichier à scanner", command=open_file)
    button_open.pack(pady=5)

    # Zone de drag-and-drop
    drop_area = tk.Label(root, text="Déposez un fichier ici", bg="lightgrey", width=70, height=4)
    drop_area.pack(pady=10)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop_file)

    second_page_button = tk.Button(root, text="Go to second page", command=second_page)
    second_page_button.pack(pady=10)
    # Lancement de l'application
    root.mainloop()

def sauvegarde_du_path(gui_daemon_process: multiprocessing.Process):
    """Save the new path."""
    # new_path = path_space.get("1.0", tk.END).strip()
    new_path = filedialog.askdirectory()
    gui_daemon_process = update_daemon_path(new_path, gui_daemon_process)

    # Redéfinir le bouton pour utiliser le nouveau processus
    path_accept.config(text="Voulez-vous changer le path à nouveau ?",
                        command=lambda: sauvegarde_du_path(gui_daemon_process))
    
    # Mettre à jour le path affiché
    path_space.delete("1.0", tk.END)
    path_space.insert("1.0", new_path)

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

def second_page():
    second_page = tk.Toplevel(root)
    second_page.title("Second page")
    second_page.geometry("800x600")
    second_page_label = tk.Label(second_page, text="This is the second page")
    second_page_label.pack(pady=10)
    app=DirectoryTreeViewer(second_page)
    app.display_directory_tree(path)

    footer_frame = tk.Frame(second_page)
    footer_frame.pack(side=tk.BOTTOM, pady=10)

    back_button = tk.Button(footer_frame, text="back", command=start_gui)
    back_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(footer_frame, text="next", command=thrid_page)
    next_button.pack(side=tk.LEFT, padx=10)

    # Bouton d'acceptation de la proposition
    third_page_button = tk.Button(footer_frame, text="Accept", command=thrid_page)
    third_page_button.pack(side=tk.LEFT,padx=10)
    

def thrid_page():
    third_page = tk.Toplevel(root)
    third_page.title("Third page")
    third_page.geometry("800x600")
    third_page_label = tk.Label(third_page, text="Bravo le rangement de votre fichier et votre arborecence est terminé")
    third_page_label.pack(pady=10)

    tk.Text(third_page, height=1, width=50).pack(pady=5)

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

if __name__ == "__main__":
    print("Starting GUI...")
    start_gui()
