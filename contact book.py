# Unique Code: PYCONBOOK_TK_V1_20231027
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import re # For basic validation

CONTACTS_FILE = "contacts_data.json"
UNIQUE_CODE = "PYCONBOOK_TK_V1_20231027"

# --- Data Handling (similar to console version) ---
def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Could not decode contacts file. Starting fresh.")
            return []
    return []

def save_contacts(contacts_list):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts_list, f, indent=4)

def validate_phone(phone):
    return bool(re.match(r"^[\d\s\-\(\)\+]+$", phone)) if phone else True # Allow empty

def validate_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email)) if email else True # Allow empty

# --- Global Variables ---
contacts = load_contacts()
selected_contact_original_index = None # Index in the main 'contacts' list

# --- GUI Functions ---
def populate_listbox(display_list=None):
    """Populates the listbox with contacts.
    If display_list is None, uses the global 'contacts' list."""
    global contacts
    current_list = display_list if display_list is not None else contacts

    listbox_contacts.delete(0, tk.END)
    for idx, contact in enumerate(current_list):
        listbox_contacts.insert(tk.END, f"{contact['name']} - {contact['phone']}")
    clear_entry_fields(deselect_listbox=False) # Keep selection if any

def on_contact_select(event):
    global selected_contact_original_index
    widget = event.widget
    selected_indices = widget.curselection()
    if not selected_indices:
        selected_contact_original_index = None
        clear_entry_fields(deselect_listbox=False)
        return

    listbox_index = selected_indices[0]
    selected_display_text = widget.get(listbox_index)

    # Find the actual contact in the global 'contacts' list
    # This is important if the listbox is showing filtered results
    found_contact = None
    original_idx_temp = -1
    for idx, c in enumerate(contacts):
        if f"{c['name']} - {c['phone']}" == selected_display_text:
            found_contact = c
            original_idx_temp = idx
            break

    if found_contact:
        selected_contact_original_index = original_idx_temp
        name_var.set(found_contact['name'])
        phone_var.set(found_contact['phone'])
        email_var.set(found_contact['email'])
        address_var.set(found_contact['address'])
    else:
        # Should not happen if listbox content is derived from 'contacts'
        selected_contact_original_index = None
        clear_entry_fields(deselect_listbox=False)


def clear_entry_fields(deselect_listbox=True):
    global selected_contact_original_index
    name_var.set("")
    phone_var.set("")
    email_var.set("")
    address_var.set("")
    selected_contact_original_index = None
    if deselect_listbox and listbox_contacts.curselection():
        listbox_contacts.selection_clear(0, tk.END)

def add_contact_gui():
    global contacts
    name = name_var.get().strip()
    phone = phone_var.get().strip()
    email = email_var.get().strip()
    address = address_var.get().strip()

    if not name:
        messagebox.showerror("Validation Error", "Name cannot be empty.")
        return
    if not phone:
        messagebox.showerror("Validation Error", "Phone cannot be empty.")
        return
    if not validate_phone(phone):
        messagebox.showerror("Validation Error", "Invalid phone number format.")
        return
    if email and not validate_email(email):
        messagebox.showerror("Validation Error", "Invalid email format.")
        return

    # Check for duplicate names (optional)
    if any(c['name'].lower() == name.lower() for c in contacts):
        messagebox.showwarning("Duplicate", f"A contact with the name '{name}' already exists.")
        return

    new_contact = {"name": name, "phone": phone, "email": email, "address": address}
    contacts.append(new_contact)
    contacts.sort(key=lambda c: c['name'].lower()) # Keep sorted
    save_contacts(contacts)
    populate_listbox()
    messagebox.showinfo("Success", f"Contact '{name}' added successfully.")
    clear_entry_fields()

def update_contact_gui():
    global contacts, selected_contact_original_index

    if selected_contact_original_index is None or selected_contact_original_index >= len(contacts):
        messagebox.showerror("Selection Error", "Please select a contact from the list to update.")
        return

    name = name_var.get().strip()
    phone = phone_var.get().strip()
    email = email_var.get().strip()
    address = address_var.get().strip()

    if not name:
        messagebox.showerror("Validation Error", "Name cannot be empty.")
        return
    if not phone:
        messagebox.showerror("Validation Error", "Phone cannot be empty.")
        return
    if not validate_phone(phone):
        messagebox.showerror("Validation Error", "Invalid phone number format.")
        return
    if email and not validate_email(email):
        messagebox.showerror("Validation Error", "Invalid email format.")
        return

    # Check for duplicate names if name changed
    original_name = contacts[selected_contact_original_index]['name']
    if name.lower() != original_name.lower():
        if any(c['name'].lower() == name.lower() and i != selected_contact_original_index for i, c in enumerate(contacts)):
            messagebox.showwarning("Duplicate", f"Another contact with the name '{name}' already exists.")
            return

    contacts[selected_contact_original_index] = {
        "name": name, "phone": phone, "email": email, "address": address
    }
    contacts.sort(key=lambda c: c['name'].lower()) # Keep sorted
    save_contacts(contacts)
    populate_listbox() # This will clear selection, so re-select if possible or clear fields
    messagebox.showinfo("Success", f"Contact '{name}' updated successfully.")
    clear_entry_fields() # Also clears selected_contact_original_index

def delete_contact_gui():
    global contacts, selected_contact_original_index

    if selected_contact_original_index is None or selected_contact_original_index >= len(contacts):
        messagebox.showerror("Selection Error", "Please select a contact from the list to delete.")
        return

    contact_to_delete = contacts[selected_contact_original_index]
    confirm = messagebox.askyesno("Confirm Delete",
                                  f"Are you sure you want to delete '{contact_to_delete['name']}'?")
    if confirm:
        contacts.pop(selected_contact_original_index)
        save_contacts(contacts)
        populate_listbox()
        messagebox.showinfo("Success", f"Contact '{contact_to_delete['name']}' deleted.")
        clear_entry_fields() # Also clears selected_contact_original_index

def search_contact_gui():
    global contacts
    search_term = simpledialog.askstring("Search Contact", "Enter name or phone to search:")
    if search_term is None: # User cancelled
        return
    search_term = search_term.strip().lower()
    if not search_term:
        messagebox.showinfo("Search", "Please enter a search term.")
        populate_listbox(contacts) # Show all if search term is empty
        return

    found_contacts = [
        c for c in contacts
        if search_term in c['name'].lower() or search_term in c['phone']
    ]

    if not found_contacts:
        messagebox.showinfo("Search Result", f"No contacts found matching '{search_term}'.")
        listbox_contacts.delete(0, tk.END) # Clear listbox
    else:
        populate_listbox(found_contacts)
        messagebox.showinfo("Search Result", f"Found {len(found_contacts)} contact(s).")
    # Note: selection made from a filtered list needs careful handling for update/delete
    # The on_contact_select logic now handles finding the original contact.
    clear_entry_fields(deselect_listbox=False) # Don't clear listbox selection

def show_all_contacts_gui():
    populate_listbox(contacts)
    clear_entry_fields()


# --- Main Window Setup ---
root = tk.Tk()
root.title(f"Tkinter Contact Book - {UNIQUE_CODE}")
root.geometry("650x500")
root.resizable(False, False)

# Style
style = ttk.Style()
style.theme_use('clam') # or 'alt', 'default', 'classic'

# --- Variables for Entry Fields ---
name_var = tk.StringVar()
phone_var = tk.StringVar()
email_var = tk.StringVar()
address_var = tk.StringVar()

# --- UI Layout ---

# Frame for input fields
input_frame = ttk.LabelFrame(root, text="Contact Details", padding=(10, 5))
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
input_frame.columnconfigure(1, weight=1) # Make entry fields expand

ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_name = ttk.Entry(input_frame, textvariable=name_var, width=40)
entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(input_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_phone = ttk.Entry(input_frame, textvariable=phone_var, width=40)
entry_phone.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(input_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_email = ttk.Entry(input_frame, textvariable=email_var, width=40)
entry_email.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(input_frame, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_address = ttk.Entry(input_frame, textvariable=address_var, width=40)
entry_address.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Frame for buttons
button_frame = ttk.Frame(root, padding=(10, 10))
button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
# Make buttons spread out a bit
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)
button_frame.columnconfigure(3, weight=1)
button_frame.columnconfigure(4, weight=1)


btn_add = ttk.Button(button_frame, text="Add Contact", command=add_contact_gui)
btn_add.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

btn_update = ttk.Button(button_frame, text="Update Contact", command=update_contact_gui)
btn_update.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

btn_delete = ttk.Button(button_frame, text="Delete Contact", command=delete_contact_gui)
btn_delete.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

btn_search = ttk.Button(button_frame, text="Search", command=search_contact_gui)
btn_search.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

btn_clear = ttk.Button(button_frame, text="Clear Fields", command=clear_entry_fields)
btn_clear.grid(row=0, column=4, padx=5, pady=5, sticky="ew")


# Frame for Listbox and "Show All" button
list_frame = ttk.LabelFrame(root, text="Contact List", padding=(10, 5))
list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
list_frame.rowconfigure(0, weight=1) # Make listbox expand
list_frame.columnconfigure(0, weight=1) # Make listbox expand

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
listbox_contacts = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, exportselection=False)
scrollbar.config(command=listbox_contacts.yview)

listbox_contacts.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

listbox_contacts.bind('<<ListboxSelect>>', on_contact_select)

btn_show_all = ttk.Button(list_frame, text="Show All / Refresh", command=show_all_contacts_gui)
btn_show_all.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


# Configure main window grid to make list_frame expand
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

# --- Initial Population ---
contacts.sort(key=lambda c: c['name'].lower()) # Sort initially
populate_listbox()

# --- Start GUI ---
if __name__ == "__main__":
    # Simple check for unique code (more for prompt adherence)
    try:
        with open(__file__, 'r') as f_script:
            script_content = f_script.read()
        if UNIQUE_CODE not in script_content:
            messagebox.showerror("Integrity Check", "Unique code missing from script!")
            root.destroy() # Or exit()
    except Exception as e:
        print(f"Could not perform unique code check: {e}") # Non-fatal for running

    root.mainloop()