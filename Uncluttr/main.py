import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
import fitz  # PyMuPDF

def open_file():
    """Ouvre un fichier via un explorateur et affiche son contenu."""
    file_path = filedialog.askopenfilename(title="Choisir un fichier")
    if file_path:
        try :
            with open(file_path, "r", encoding="utf-16") as file:
                content = file.read()
            text_area.delete("1.0", tk.END)  # Efface le contenu précédent
            text_area.insert(tk.END, content)
        except Exception as e:
            pdf_document = fitz.open(file_path)
            content = ""
            for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    content += page.get_text()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, content)
            
def drop_file(event):
    """Récupère le chemin du fichier déposé et affiche son contenu."""
    file_path = event.data.strip()
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, content)
        except Exception as e:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, f"Erreur lors de l'ouverture du fichier : {e}")

# Fenêtre principale
root = tk.Tk()
root.title("Application Drag and Drop")
root.geometry("600x400")

# Zone de texte pour afficher le contenu du fichier
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
text_area.pack(pady=10)

# Bouton pour ouvrir un fichier
button_open = tk.Button(root, text="Ouvrir un fichier", command=open_file)
button_open.pack(pady=5)

# Zone de drag-and-drop
drop_area = tk.Label(root, text="Déposez un fichier ici", bg="lightgrey", width=50, height=2)
drop_area.pack(pady=10)

# Configuration de drag-and-drop (nécessite `tkinterdnd2`)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    root = TkinterDnD.Tk()  # Initialise le support Drag and Drop
    drop_area = tk.Label(root, text="Déposez un fichier ici", bg="lightgrey", width=50, height=2)
    drop_area.pack(pady=10)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop_file)
except ImportError:
    drop_area.config(text="Installez tkinterdnd2 pour activer le drag-and-drop")

# Lancement de l'application
root.mainloop()
