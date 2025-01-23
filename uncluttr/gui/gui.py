import configparser, sys, os, shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

def start_gui():
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
    
    # Espace pour path
    path_label = tk.Label(root, text="Le path actuel pour le daemon est :")
    path_space.insert(tk.INSERT,path)
    # Bouton pour le changement de path
    path_accept = tk.Button(root, text="Voulez-vous changer le path pour le daemon ?",command=sauvegarde_du_path)
    
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
    
    # Boutton d'accpetation de la proposition
    third_page_button = tk.Button(footer_frame, text="Accept", command=thrid_page)
    third_page_button.pack(side=tk.LEFT,padx=10)
    
def thrid_page():
    third_page = tk.Toplevel(root)
    third_page.title("Third page")
    third_page.geometry("800x600")
    third_page_label = tk.Label(third_page, text="Bravo le rangement de votre fichier et votre arborecence est terminé")
    third_page_label.pack(pady=10)
    
    tk.Text(third_page, height=1, width=50).pack(pady=5)

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