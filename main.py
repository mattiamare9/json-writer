import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

def bind_enter_to_buttons(widget):
    if isinstance(widget, tk.Button):
        widget.bind("<Return>", lambda event: widget.invoke())
    for child in widget.winfo_children():
        bind_enter_to_buttons(child)

def add_entry():
    key = key_entry.get()
    value = value_entry.get()

    if not key:
        messagebox.showwarning("Errore", "La chiave non può essere vuota!")
        return

    # Try to parse the value as a number, list, or dictionary
    try:
        parsed_value = eval(value)
    except:
        parsed_value = value  # Treat as a string

    try:
        selected_item = tree.selection()[0]
        parent_path = tree.item(selected_item, "text")
        keys = get_full_key_path(selected_item)
        nested_dict = get_nested_dict(data, keys)
        if isinstance(nested_dict, dict):
            nested_dict[key] = parsed_value
        else:
            messagebox.showwarning("Errore", "L'elemento selezionato non è un dizionario!")
            return
    except IndexError:  # No selection, add to root
        data[key] = parsed_value

    update_treeview()
    key_entry.delete(0, tk.END)
    value_entry.delete(0, tk.END)

def remove_entry():
    try:
        selected_item = tree.selection()[0]
        keys = get_full_key_path(selected_item)
        if not keys:
            messagebox.showwarning("Errore", "Seleziona un elemento valido da rimuovere!")
            return

        if len(keys) == 1:  # Remove from root
            del data[keys[0]]
        else:  # Remove from a nested dictionary
            nested_dict = get_nested_dict(data, keys[:-1])
            del nested_dict[keys[-1]]

        update_treeview()
    except IndexError:
        messagebox.showwarning("Errore", "Seleziona un elemento da rimuovere!")

def move_item_up():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Errore", "Seleziona un elemento da spostare!")
        return

    item_id = selected_item[0]
    parent_id = tree.parent(item_id)
    siblings = tree.get_children(parent_id)
    index = siblings.index(item_id)

    if index > 0:  # Se non è il primo
        swap_items(parent_id, index, index - 1)

def move_item_down():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Errore", "Seleziona un elemento da spostare!")
        return

    item_id = selected_item[0]
    parent_id = tree.parent(item_id)
    siblings = tree.get_children(parent_id)
    index = siblings.index(item_id)

    if index < len(siblings) - 1:  # Se non è l'ultimo
        swap_items(parent_id, index, index + 1)

def swap_items(parent_id, index1, index2):
    siblings = tree.get_children(parent_id)
    keys = get_full_key_path(siblings[index1])[:-1]
    nested_dict = get_nested_dict(data, keys)

    # Scambia i valori nel dizionario
    keys_at_level = list(nested_dict.keys())
    key1, key2 = keys_at_level[index1], keys_at_level[index2]
    nested_dict[key1], nested_dict[key2] = nested_dict[key2], nested_dict[key1]

    update_treeview()  # Aggiorna la visualizzazione

def get_expanded_nodes(tree):
    """Recursively collect IDs of expanded nodes."""
    expanded_nodes = []

    def collect_expanded(node):
        if tree.item(node, "open"):
            expanded_nodes.append(node)
        for child in tree.get_children(node):
            collect_expanded(child)

    collect_expanded("")  # Start from the root
    return expanded_nodes


def restore_expanded_nodes(tree, expanded_nodes):
    """Re-expand previously expanded nodes."""
    for node in expanded_nodes:
        if tree.exists(node):
            tree.item(node, open=True)

# def update_treeview():
#     tree.delete(*tree.get_children())  # Clear the tree
#     display_tree(data)

def update_treeview():
    """Update the Treeview while preserving expanded nodes."""
    expanded_nodes = get_expanded_nodes(tree)  # Save expanded state

    # Clear and rebuild the tree
    tree.delete(*tree.get_children())
    display_tree(data)

    restore_expanded_nodes(tree, expanded_nodes)  # Restore expanded state



def display_tree(d, parent=""):
    """Display a nested dictionary in the treeview."""
    for key, value in d.items():
        if isinstance(value, dict):
            node_id = tree.insert(parent, "end", text=key, values=["(dict)"])
            display_tree(value, node_id)  # Handle sub-dictionaries
        elif isinstance(value, list):
            node_id = tree.insert(parent, "end", text=key, values=["(list)"])
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    item_id = tree.insert(node_id, "end", text=f"[{i}]", values=["(dict)"])
                    display_tree(item, item_id)
                else:
                    tree.insert(node_id, "end", text=f"[{i}]", values=[repr(item)])
        else:
            tree.insert(parent, "end", text=key, values=[repr(value)])

def get_full_key_path(node_id):
    """Get the full key path for a given Treeview node."""
    path = []
    while node_id:
        path.insert(0, tree.item(node_id, "text"))
        node_id = tree.parent(node_id)
    return path

def get_nested_dict(d, keys):
    """Return the nested dictionary for a given path of keys."""
    for key in keys:
        d = d[key]
    return d

def save_json():
    if not data:
        messagebox.showwarning("Errore", "Non ci sono dati da salvare!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Salvato", "File JSON salvato con successo!")

def load_json():
    global data
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path and os.path.splitext(file_path)[1] == ".json":
        try:
            with open(file_path, 'r') as file:
                loaded_data = json.load(file)
                if isinstance(loaded_data, dict):
                    data = loaded_data
                    update_treeview()
                    messagebox.showinfo("Caricato", "File JSON caricato con successo!")
                else:
                    messagebox.showerror("Errore", "Il file JSON deve contenere un oggetto di tipo dizionario!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il caricamento del file JSON: {e}")
    else:
        messagebox.showwarning("Errore", "Seleziona un file JSON valido!")

def deselect_item(event):
    tree.selection_remove(tree.selection())

def get_value_for_key_path(item_id):
    # Get the full key path for the item
    full_key_path = get_full_key_path(item_id)
    
    # Traverse the nested dictionary or list to get the value
    value = data
    for key in full_key_path:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list):
            index = int(key[1:-1])  # Convert '[i]' to integer index
            value = value[index]
    
    return value

def show_full_name(event):
    item_id = tree.identify_row(event.y)
    if item_id:
        full_key = get_full_key_path(item_id)[-1]
        value = get_value_for_key_path(item_id)
        tooltip_label.config(text=f"{full_key}: {repr(value)}")
    else:
        tooltip_label.config(text="")


# Data storage
data = {}

# GUI Setup
root = tk.Tk()
root.title("JSON Builder con Visualizzazione ad Albero")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Chiave:").grid(row=0, column=0, sticky=tk.W)
key_entry = tk.Entry(frame, width=30)
key_entry.grid(row=0, column=1)

tk.Label(frame, text="Valore (stringa, numero, lista, dizionario):").grid(row=1, column=0, sticky=tk.W)
value_entry = tk.Entry(frame, width=30)
value_entry.grid(row=1, column=1)

add_button = tk.Button(frame, text="Aggiungi", command=add_entry)
add_button.grid(row=2, column=0, pady=5)

remove_button = tk.Button(frame, text="Rimuovi selezionato", command=remove_entry)
remove_button.grid(row=2, column=1, pady=5)

tree = ttk.Treeview(frame, columns=("Type"), show="tree")
tree.heading("#0", text="Chiave")
tree.heading("Type", text="Tipo")
tree.grid(row=3, column=0, columnspan=2, pady=5)

# Deselect item when clicking outside any node
tree.bind("<Button-1>", deselect_item)

tooltip_label = tk.Label(root, text="", fg="blue")
tooltip_label.pack(side=tk.BOTTOM)
tree.bind("<Motion>", show_full_name)


load_button = tk.Button(frame, text="Carica JSON", command=load_json)
load_button.grid(row=4, column=1, pady=5)

save_button = tk.Button(frame, text="Salva come JSON", command=save_json)
save_button.grid(row=5, column=1, pady=5)

up_button = tk.Button(frame, text="Sposta Su", command=move_item_up)
up_button.grid(row=4, column=0, pady=5)

down_button = tk.Button(frame, text="Sposta Giù", command=move_item_down)
down_button.grid(row=5, column=0, pady=5)

bind_enter_to_buttons(root)

root.mainloop()