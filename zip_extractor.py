import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style, Treeview
import os
import time
import zipfile
import rarfile

def get_folders_and_archives(path):
    folders = []
    archives = []
    for entry in os.scandir(path):
        if entry.is_dir():
            folders.append(entry.name)
        elif entry.name.lower().endswith((".zip", ".rar", ".7z")):
            archives.append(entry.name)
    return folders, archives

def browse_folders():
    folder_path = filedialog.askdirectory(title="Select a folder")
    if not folder_path:
        return

    folder_var.set(folder_path)
    folders, archives = get_folders_and_archives(folder_path)

    tree.delete(*tree.get_children())
    for folder in folders:
        tree.insert("", "end", values=(folder,))
    for archive in archives:
        tree.insert("", "end", values=(archive,))

def extract_archive():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select an archive file.")
        return

    folder_path = folder_var.get()
    if not folder_path:
        messagebox.showwarning("No Folder", "Please select a folder to extract the archive.")
        return

    selected_item = tree.item(selected_items[0])
    file_name = selected_item["values"][0]
    file_path = os.path.join(folder_path, file_name)

    try:
        extracted_folder = filedialog.askdirectory(title="Select an output folder for extraction")
        if not extracted_folder:
            return

        if file_name.lower().endswith(".zip"):
            archive = zipfile.ZipFile(file_path, 'r')
            file_list = archive.namelist()

        elif file_name.lower().endswith((".rar", ".7z")):
            archive = rarfile.RarFile(file_path, 'r')
            file_list = archive.namelist()

        else:
            messagebox.showerror("Unsupported Format", "The selected file format is not supported.")
            return

        total_files = len(file_list)

        progress_var = tk.DoubleVar()
        progress = Progressbar(root, style="Custom.Horizontal.TProgressbar", mode='determinate', length=500, variable=progress_var)
        progress.pack(pady=20)

        def update_progress(index):
            if index < total_files:
                file = file_list[index]
                progress_val = (index / total_files) * 100
                progress['value'] = progress_val
                elapsed_time = time.time() - start_time
                average_time_per_file = elapsed_time / index if index > 0 else 0
                remaining_files = total_files - index
                estimated_time = average_time_per_file * remaining_files
                time_label.config(text=f"Extracting: {file}\nEstimated Time: {estimated_time:.2f} seconds")
                root.update_idletasks()
                root.after(100, extract_task, index + 1)

        def extract_task(index):
            if index < total_files:
                file = file_list[index]
                archive.extract(file, extracted_folder)
                extracted_files.append(file)
                update_progress(index)

            else:
                archive.close()  # Close the archive file after extraction
                messagebox.showinfo("Extraction Successful", "Archive extracted successfully!")

        est_time_frame = tk.Frame(root)
        est_time_frame.pack()
        time_label = tk.Label(est_time_frame, text="Estimated Time: N/A")
        time_label.pack(pady=5)

        progress = Progressbar(root, style="Custom.Horizontal.TProgressbar", mode='determinate', length=500)
        progress.pack(pady=20)

        extracted_files = []
        start_time = time.time()
        extract_task(0)

    except Exception as e:
        messagebox.showerror("Extraction Error", f"An error occurred: {e}")

# Create the main application window
root = tk.Tk()
root.title("Folder and Archive Viewer")
root.geometry("800x500")

# Set the icon for the application window
root.iconbitmap("icon.ico")  # Replace "icon.ico" with the actual path to your icon file

# Create a style for the custom progress bar
style = Style()
style.theme_use('clam')
style.configure("Custom.Horizontal.TProgressbar", troughcolor="white", background="blue", thickness=5)

# Variable to store the selected folder path
folder_var = tk.StringVar()

# Button to browse folders
browse_button = tk.Button(root, text="Browse Folders", command=browse_folders)
browse_button.pack(pady=10)

# Entry to show the selected folder path
folder_entry = tk.Entry(root, textvariable=folder_var, state='readonly', width=50)
folder_entry.pack(pady=5)

# Create a Treeview widget to display the folder and archive files
tree = Treeview(root, columns=("Name",), show="headings")
tree.heading("#1", text="Name")
tree.pack(fill=tk.BOTH, expand=True)

# Create a button to trigger the extraction process
extract_button = tk.Button(root, text="Extract Archive", command=extract_archive)
extract_button.pack(pady=10)

# Start the main event loop
root.mainloop()
