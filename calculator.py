# Unique Code ID: TKCALC_BASIC_GUI_V1_20231027

import tkinter as tk
from tkinter import messagebox # For potential error popups (optional, here we display in label)
import math # For checking if float is integer

def calculate():
    """
    Gets values from entry fields, performs calculation based on selected
    operation, and updates the result label. Handles potential errors.
    """
    try:
        num1_str = entry_num1.get()
        num2_str = entry_num2.get()

        # Validate and convert inputs
        num1 = float(num1_str)
        num2 = float(num2_str)

        operation = operation_var.get() # Get selected operation from radio button

        result = None

        # Perform calculation
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                result_var.set("Error: Division by zero")
                # messagebox.showerror("Error", "Division by zero is not allowed.")
                return # Stop calculation
            else:
                result = num1 / num2
        else:
            # This case should ideally not be reached with radio buttons
            result_var.set("Error: Invalid operation")
            return

        # Format and display result
        if result is not None:
             # Format nicely, removing trailing .0 for whole numbers
            if isinstance(result, float) and result.is_integer():
                result_var.set(f"Result: {int(result)}")
            else:
                 result_var.set(f"Result: {result:.4f}") # Format float

    except ValueError:
        result_var.set("Error: Invalid number input")
        # messagebox.showerror("Error", "Please enter valid numbers.")
    except Exception as e:
        result_var.set(f"An unexpected error occurred: {e}")
        # messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# --- Setup Main Window ---
root = tk.Tk()
root.title("Simple Tkinter Calculator")
root.geometry("300x250") # Set a fixed window size (width x height)
root.resizable(False, False) # Prevent resizing

# --- Variables ---
# StringVar to hold the selected operation
operation_var = tk.StringVar(value='+') # Default to addition
# StringVar to display the result or errors
result_var = tk.StringVar(value="Result: ")

# --- Widgets ---

# Number 1 Input
label_num1 = tk.Label(root, text="First Number:")
entry_num1 = tk.Entry(root, width=20)

# Number 2 Input
label_num2 = tk.Label(root, text="Second Number:")
entry_num2 = tk.Entry(root, width=20)

# Operation Selection Frame (to group radio buttons)
op_frame = tk.Frame(root)
label_op = tk.Label(op_frame, text="Operation:")

# Radio Buttons for Operations
radio_add = tk.Radiobutton(op_frame, text="+", variable=operation_var, value='+')
radio_sub = tk.Radiobutton(op_frame, text="-", variable=operation_var, value='-')
radio_mul = tk.Radiobutton(op_frame, text="*", variable=operation_var, value='*')
radio_div = tk.Radiobutton(op_frame, text="/", variable=operation_var, value='/')

# Calculate Button
calc_button = tk.Button(root, text="Calculate", command=calculate, width=15)

# Result Display Label
result_label = tk.Label(root, textvariable=result_var, relief=tk.SUNKEN, width=25, anchor='w') # anchor='w' aligns text left

# --- Layout using grid ---
label_num1.grid(row=0, column=0, padx=10, pady=5, sticky='w')
entry_num1.grid(row=0, column=1, padx=10, pady=5)

label_num2.grid(row=1, column=0, padx=10, pady=5, sticky='w')
entry_num2.grid(row=1, column=1, padx=10, pady=5)

# Place the operation frame and its contents
op_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
label_op.pack(side=tk.LEFT, padx=10) # Use pack within the frame
radio_add.pack(side=tk.LEFT)
radio_sub.pack(side=tk.LEFT)
radio_mul.pack(side=tk.LEFT)
radio_div.pack(side=tk.LEFT)

calc_button.grid(row=3, column=0, columnspan=2, pady=15) # Span across columns

result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew') # sticky='ew' makes it stretch horizontally

# --- Start the Tkinter event loop ---
root.mainloop()