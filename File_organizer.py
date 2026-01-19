"""
File Organizer Application.
Organizes files in a directory into subfolders based on file extensions.
"""
import os
import shutil
import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# Default categories and ignore list
default_config = {
    "categories": {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.odt', '.rtf', '.csv'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2'],
        'Scripts': ['.py', '.js', '.sh', '.bat', '.rb', '.php', '.html', '.css'],
        'Executables': ['.exe', '.msi', '.dmg', '.app'],
        'Fonts': ['.ttf', '.otf', '.woff', '.woff2'],
        'Torrents': ['.torrent']
    },
    "ignore": ['desktop.ini', 'Thumbs.db', '.DS_Store']  # Files to ignore entirely
}

CONFIG_FILE = 'config.json'
selected_directory = None
undo_stack = []

# Setup logging
logging.basicConfig(filename='organizer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load or create config
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

file_extensions = config['categories']
ignore_list = [item.lower() for item in config['ignore']]

def save_config():
    """Save current configuration to JSON file."""
    config['categories'] = file_extensions
    config['ignore'] = ignore_list
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def open_config_window():
    """Open a window to configure categories and extensions."""
    config_win = tk.Toplevel(root)
    config_win.title("Configure Categories")
    config_win.geometry("600x500")
    config_win.resizable(True, True)

    # Main Frame
    config_panel = ttk.Frame(config_win, padding="10")
    config_panel.pack(fill=tk.BOTH, expand=True)

    # Categories Section
    cat_frame = ttk.LabelFrame(config_panel, text="Categories", padding="5")
    cat_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    categories_listbox = tk.Listbox(cat_frame, height=15)
    categories_listbox.pack(fill=tk.BOTH, expand=True)
    for cat in file_extensions.keys():
        categories_listbox.insert(tk.END, cat)

    # Extensions Section
    ext_frame = ttk.LabelFrame(config_panel, text="Extensions for Selected Category", padding="5")
    ext_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    extensions_frame = ttk.Frame(ext_frame)
    extensions_frame.pack(fill=tk.BOTH, expand=True)

    ext_vars = []  # List of (ext, var) tuples

    def update_extensions(event=None):
        # Clear previous checkboxes
        for widget in extensions_frame.winfo_children():
            widget.destroy()
        ext_vars.clear()

        selected = categories_listbox.curselection()
        if selected:
            cat = categories_listbox.get(selected[0])
            exts = file_extensions[cat]
            for ext in exts:
                var = tk.BooleanVar(value=True)
                cb = ttk.Checkbutton(extensions_frame, text=ext, variable=var)
                cb.pack(anchor='w', pady=2)
                ext_vars.append((ext, var))

    categories_listbox.bind('<<ListboxSelect>>', update_extensions)

    # Buttons Frame
    btn_frame = ttk.Frame(config_win, padding="5")
    btn_frame.pack(fill=tk.X)

    def add_category():
        new_cat = simpledialog.askstring("Add Category", "Enter category name:")
        if new_cat and new_cat not in file_extensions:
            file_extensions[new_cat] = []
            categories_listbox.insert(tk.END, new_cat)
            save_config()
            status_var.set(f"Added category: {new_cat}")

    def remove_category():
        selected = categories_listbox.curselection()
        if selected:
            cat = categories_listbox.get(selected[0])
            if messagebox.askyesno("Confirm", f"Remove category '{cat}'?"):
                del file_extensions[cat]
                categories_listbox.delete(selected[0])
                # Clear extensions
                for widget in extensions_frame.winfo_children():
                    widget.destroy()
                ext_vars.clear()
                save_config()
                status_var.set(f"Removed category: {cat}")

    def add_extension():
        selected = categories_listbox.curselection()
        if selected:
            cat = categories_listbox.get(selected[0])
            new_ext = simpledialog.askstring("Add Extension", "Enter extension (e.g., .txt):")
            if new_ext and new_ext not in file_extensions[cat]:
                file_extensions[cat].append(new_ext)
                save_config()
                update_extensions()  # Refresh checkboxes
                status_var.set(f"Added extension {new_ext} to {cat}")

    def save_extensions():
        selected = categories_listbox.curselection()
        if selected:
            cat = categories_listbox.get(selected[0])
            file_extensions[cat] = [ext for ext, var in ext_vars if var.get()]
            save_config()
            status_var.set(f"Saved extensions for {cat}")

    ttk.Button(btn_frame, text="Add Category", command=add_category).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(btn_frame, text="Remove Category", command=remove_category).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(btn_frame, text="Add Extension", command=add_extension).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(btn_frame, text="Save Extensions", command=save_extensions).grid(row=0, column=3, padx=5, pady=5)

    ttk.Button(config_win, text="Close", command=config_win.destroy).pack(pady=5)

def select_directory():
    """Open dialog to select the target directory."""
    dir_path = filedialog.askdirectory(title="Select Directory to Organize")
    if dir_path:
        directory_label.config(text=f"Selected Directory: {dir_path}")
        global selected_directory
        selected_directory = dir_path
        status_var.set(f"Selected directory: {os.path.basename(dir_path)}")

def undo_changes():
    """Revert the last batch of organized files."""
    if not undo_stack:
        return

    last_batch = undo_stack.pop()
    undo_count = 0
    output_text.insert(tk.END, "\n--- Undoing Last Operation ---\n")

    for src, dest in last_batch:
        try:
            if os.path.exists(dest):
                shutil.move(dest, src)
                undo_count += 1
                logging.info(f"Undid move: {dest} -> {src}")
            else:
                logging.warning(f"Undo failed: File not found at {dest}")
        except OSError as e:
            logging.error(f"Undo error {dest} -> {src}: {e}")
            output_text.insert(tk.END, f"Error undoing {os.path.basename(dest)}: {e}\n")

    output_text.insert(tk.END, f"Successfully reverted {undo_count} files.\n")
    status_var.set(f"Undid {undo_count} moves.")
    if not undo_stack:
        undo_btn.config(state=tk.DISABLED)

def organize_files():
    """Main logic to organize files into subfolders."""
    if not selected_directory:
        messagebox.showerror("Error", "Please select a directory first.")
        return

    dry_run = dry_run_var.get()
    output_text.delete(1.0, tk.END)  # Clear previous output
    status_var.set("Organizing files...")

    current_batch = []
    # Create Subdirectories Based On File Types
    for folder in file_extensions.keys():
        folder_path = os.path.join(selected_directory, folder)
        if not os.path.exists(folder_path):
            if not dry_run:
                os.makedirs(folder_path)
            output_text.insert(tk.END, f"Created folder: {folder}\n")

    # Move Files To Their Respective Subdirectories
    organized_counts = {folder: 0 for folder in file_extensions.keys()}
    for filename in os.listdir(selected_directory):
        file_path = os.path.join(selected_directory, filename)
        if os.path.isfile(file_path):
            # Skip ignored files and hidden files
            if filename.lower() in ignore_list or filename.startswith('.'):
                continue
            moved = False
            for folder, extensions in file_extensions.items():
                if any(filename.lower().endswith(ext) for ext in extensions):
                    target_path = os.path.join(selected_directory, folder, filename)
                    if dry_run:
                        output_text.insert(tk.END, f"Would move: {filename} to {folder}\n")
                    else:
                        try:
                            shutil.move(file_path, target_path)
                            current_batch.append((file_path, target_path))
                            logging.info(f"Moved {filename} to {folder}")
                        except OSError as e:
                            logging.error(f"Error moving {filename}: {e}")
                            output_text.insert(tk.END, f"Error moving {filename}: {str(e)}\n")
                            continue
                    organized_counts[folder] += 1
                    moved = True
                    break

            # Notify if a file type does not match any category
            if not moved:
                output_text.insert(tk.END, f'No category found for file: {filename}\n')

    # Itemized Summary
    organized_count = sum(organized_counts.values())
    if organized_count == 0:
        output_text.insert(tk.END, f'Total files organized: {organized_count}\n')
    else:
        output_text.insert(tk.END, f'Total files organized: {organized_count}\n')
        output_text.insert(tk.END, 'Files have been organized into the following categories:\n')
        for folder, count in organized_counts.items():
            if count > 0:
                output_text.insert(tk.END, f'{folder}: {count} files\n')

    if current_batch:
        undo_stack.append(current_batch)
        undo_btn.config(state=tk.NORMAL)

    status_var.set("Organization complete.")

# GUI Setup
root = tk.Tk()
root.title("Ice's File Organizer")
root.geometry("700x500")
root.resizable(True, True)

# Menu Bar
menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Select Directory", command=select_directory, accelerator="Ctrl+O")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit, accelerator="Ctrl+Q")

edit_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Configure Categories", command=open_config_window, accelerator="Ctrl+C")

help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "File Organizer v1.0\nOrganize files by type with a GUI."))

# Bind shortcuts
root.bind('<Control-o>', lambda e: select_directory())
root.bind('<Control-q>', lambda e: root.quit())
root.bind('<Control-c>', lambda e: open_config_window())

# Main Frame
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Directory Selection
dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="5")
dir_frame.pack(fill=tk.X, pady=5)
ttk.Button(dir_frame, text="Select Directory", command=select_directory).pack(side=tk.LEFT, padx=5)
directory_label = ttk.Label(dir_frame, text="Selected Directory: None")
directory_label.pack(side=tk.LEFT, padx=5)

# Options
options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
options_frame.pack(fill=tk.X, pady=5)
dry_run_var = tk.BooleanVar()
ttk.Checkbutton(options_frame, text="Dry Run (Preview Only)", variable=dry_run_var).pack(side=tk.LEFT, padx=5)
ttk.Button(options_frame, text="Configure Categories", command=open_config_window).pack(side=tk.RIGHT, padx=5)

# Action Buttons
action_frame = ttk.Frame(main_frame)
action_frame.pack(pady=10)
ttk.Button(action_frame, text="Organize Files", command=organize_files).pack(side=tk.LEFT, padx=5)
undo_btn = ttk.Button(action_frame, text="Undo Last", command=undo_changes, state=tk.DISABLED)
undo_btn.pack(side=tk.LEFT, padx=5)

# Output Area with Scrollbar
output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
output_text = tk.Text(output_frame, height=10, wrap=tk.WORD)
scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=output_text.yview)
output_text.config(yscrollcommand=scrollbar.set)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Status Bar
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
