import json
import os
import datetime
import tkinter as tk
from tkinter import ttk  # For themed widgets (optional but nice)
from tkinter import messagebox
from tkinter import simpledialog

TASKS_FILE = "tasks.json"

# --- Core Data Logic (Slightly modified for GUI feedback) ---

def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            # Ensure tasks have required keys, provide defaults if missing
            for task in tasks:
                task.setdefault('status', 'pending')
                task.setdefault('added_on', 'unknown')
                task.setdefault('completed_on', None)
            return tasks
    except (json.JSONDecodeError, IOError) as e:
        messagebox.showerror("Load Error", f"Error loading tasks: {e}\nStarting with an empty list.")
        return []
    except Exception as e:
        messagebox.showerror("Load Error", f"An unexpected error occurred loading tasks: {e}\nStarting empty.")
        return []


def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError as e:
        messagebox.showerror("Save Error", f"Error saving tasks: {e}")
    except Exception as e:
        messagebox.showerror("Save Error", f"An unexpected error occurred saving tasks: {e}")

# --- Tkinter GUI Application Class ---

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        self.root.geometry("600x450") # Adjusted size

        self.tasks = load_tasks()

        # Style (Optional)
        self.style = ttk.Style()
        self.style.theme_use("clam") # Or 'alt', 'default', 'classic'

        # --- GUI Elements ---
        # Frame for Listbox and Scrollbar
        self.list_frame = ttk.Frame(root)
        self.list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox
        self.task_listbox = tk.Listbox(self.list_frame, width=70, height=15,
                                       yscrollcommand=self.scrollbar.set,
                                       selectmode=tk.SINGLE, # Allow selecting only one task
                                       font=("Arial", 11))
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.task_listbox.yview)

        # Frame for Entry and Add Button
        self.entry_frame = ttk.Frame(root)
        self.entry_frame.pack(pady=5, padx=10, fill=tk.X)

        # Entry widget for adding new tasks
        self.task_entry = ttk.Entry(self.entry_frame, width=50, font=("Arial", 11))
        self.task_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.task_entry.bind("<Return>", self.add_task_gui) # Add task on Enter key

        # Add Task Button
        self.add_button = ttk.Button(self.entry_frame, text="Add Task", command=self.add_task_gui)
        self.add_button.pack(side=tk.LEFT)

        # Frame for Action Buttons
        self.action_frame = ttk.Frame(root)
        self.action_frame.pack(pady=10, padx=10, fill=tk.X)

        # Action Buttons
        self.complete_button = ttk.Button(self.action_frame, text="Mark Complete", command=self.mark_complete_gui)
        self.complete_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(self.action_frame, text="Update Task", command=self.update_task_gui)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(self.action_frame, text="Delete Task", command=self.delete_task_gui)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # --- Initial Load ---
        self.refresh_task_list()

    def refresh_task_list(self):
        """Clears and repopulates the listbox with current tasks."""
        self.task_listbox.delete(0, tk.END) # Clear existing items

        # Sort tasks: pending first, then by added date
        try:
             # Sort safely, handling potential missing or malformed dates
            self.tasks.sort(key=lambda x: (x['status'] == 'completed', x.get('added_on', '')))
        except Exception as e:
            print(f"Warning: Error during sorting - {e}") # Log sort error, but continue

        # Populate listbox
        self.task_map = {} # Map listbox index to actual task index in self.tasks
        listbox_idx = 0
        for i, task in enumerate(self.tasks):
            status_symbol = "[X]" if task.get('status', 'pending') == 'completed' else "[ ]"
            added_date = task.get('added_on', 'N/A')
            desc = task.get('description', 'No Description')
            display_text = f"{status_symbol} {desc} (Added: {added_date})"
            if task.get('status') == 'completed':
                completed_date = task.get('completed_on', 'N/A')
                display_text += f" (Completed: {completed_date})"

            self.task_listbox.insert(tk.END, display_text)
            self.task_map[listbox_idx] = i # Store mapping
            # Optional: Color completed tasks differently
            if task.get('status') == 'completed':
                self.task_listbox.itemconfig(listbox_idx, {'fg': 'gray'})
            else:
                 self.task_listbox.itemconfig(listbox_idx, {'fg': 'black'})
            listbox_idx += 1


    def add_task_gui(self, event=None): # Add event=None for Enter key binding
        """Adds a task from the entry field."""
        description = self.task_entry.get().strip()
        if description:
            new_task = {
                "description": description,
                "status": "pending",
                "added_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "completed_on": None
            }
            self.tasks.append(new_task)
            save_tasks(self.tasks)
            self.refresh_task_list()
            self.task_entry.delete(0, tk.END) # Clear entry field
            # Optional: messagebox.showinfo("Success", f"Task '{description}' added.")
        else:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")

    def get_selected_task_index(self):
        """Gets the index from the core tasks list based on listbox selection."""
        try:
            selected_listbox_indices = self.task_listbox.curselection()
            if not selected_listbox_indices:
                messagebox.showwarning("Selection Error", "Please select a task first.")
                return None
            listbox_index = selected_listbox_indices[0]
            # Use the map to find the original index in self.tasks
            original_task_index = self.task_map.get(listbox_index)
            if original_task_index is None or original_task_index >= len(self.tasks):
                 messagebox.showerror("Internal Error", "Task mapping failed. Please restart.")
                 return None
            return original_task_index
        except Exception as e:
            messagebox.showerror("Error", f"Could not get selected task: {e}")
            return None


    def mark_complete_gui(self):
        """Marks the selected task as complete."""
        task_index = self.get_selected_task_index()
        if task_index is not None:
            if self.tasks[task_index]['status'] == 'completed':
                messagebox.showinfo("Already Done", "This task is already marked as complete.")
            else:
                self.tasks[task_index]['status'] = 'completed'
                self.tasks[task_index]['completed_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                save_tasks(self.tasks)
                self.refresh_task_list()
                # Optional: messagebox.showinfo("Success", "Task marked as complete.")


    def update_task_gui(self):
        """Updates the description of the selected task."""
        task_index = self.get_selected_task_index()
        if task_index is not None:
            current_description = self.tasks[task_index]['description']
            new_description = simpledialog.askstring("Update Task",
                                                     f"Enter new description for:",
                                                     initialvalue=current_description)
            if new_description is not None: # Check if user cancelled
                new_description = new_description.strip()
                if new_description:
                     if new_description != current_description:
                        self.tasks[task_index]['description'] = new_description
                        # Optionally reset status? For now, keep status as is.
                        # self.tasks[task_index]['status'] = 'pending'
                        # self.tasks[task_index]['completed_on'] = None
                        save_tasks(self.tasks)
                        self.refresh_task_list()
                        # Optional: messagebox.showinfo("Success", "Task updated.")
                     else:
                         messagebox.showinfo("No Change", "Description is the same.")
                else:
                    messagebox.showwarning("Input Error", "New description cannot be empty.")


    def delete_task_gui(self):
        """Deletes the selected task after confirmation."""
        task_index = self.get_selected_task_index()
        if task_index is not None:
            task_desc = self.tasks[task_index]['description']
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete task:\n'{task_desc}'?"):
                del self.tasks[task_index]
                save_tasks(self.tasks)
                self.refresh_task_list()
                # Optional: messagebox.showinfo("Success", f"Task '{task_desc}' deleted.")

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()