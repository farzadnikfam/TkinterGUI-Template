# Generic data entry application with Tkinter

import tkinter as tk
import numpy as np
import pandas as pd
import os
import csv
import tkinter.font as tkFont
from tkinter import ttk, filedialog, messagebox
from tkinter import Toplevel, scrolledtext, Button

from gui_app_functions import *  # Import custom functions from a separate file


# Lists of features and outputs
top_list = ["A","B","C","D","E","F","G","H","I","J","K","L","Threshold"]
bottom_list = ['a','b','c','d','e','f','g','h','i','j','k','l','threshold']
output_list = ['output','output_flag']
total_list = bottom_list + output_list
total_list_index = ["#"] + total_list
len_list = len(top_list)
len_output = len(output_list)
len_total = len_list + len_output
entry_list = [None] * len_list
value_list = [None] * len_list
default_list = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 5])
all_scalable_widgets = []
default_font_sizes = {}
original_widget_sizes = {}

# Explanations for features
explanations = {col: f"Description for {col}" for col in bottom_list}

# Tooltip dictionary for buttons
button_tooltips = {
    "Add": "Add a new row to the table using the current input values.",
    "Copy": "Copy the selected row's values into the input fields.",
    "Edit": "Replace the selected rows with the current input values.",
    "Set Defaults": "Save the current input values as defaults.",
    "Clear Inputs": "Clear all input fields.",
    "Clear Outputs": 'Clear the calculated outputs ("output", "output_flag") in the selected rows.',
    "Clean": "Remove invalid or non-numeric values from the selected rows.",
    "Correct": "Fill missing or invalid inputs in selected rows with default values.",
    "Select All": "Select all rows in the table.",
    "Deselect All": "Unselect all currently selected rows.",
    "Delete": "Delete the selected rows permanently.",
    "▶️ Run Calculation": "Perform calculations on the selected rows.",
}

# GUI setup with Tkinter
root = tk.Tk()
root.title("Data Entry Application")  # Generic title
root.geometry("900x650")  # Window size

# Optional: icon (commented out since no domain-specific resource is needed)
# try:
#     root.iconbitmap("app_icon.ico")
# except:
#     pass

# Default font
font = tk.font.Font(size=9)





# =============================================
# Functions section
# =============================================

# Update row numbers in the Treeview
def update_row_numbers():
    for idx, item in enumerate(tree_frame.get_children(), 1):
        values = list(tree_frame.item(item, "values"))
        if values:
            values[0] = str(idx)
            tree_frame.item(item, values=values)


# Add a new row to the Treeview with values from input fields
def add_row():
    values = []
    for e in entry_list:
        val = e.get()
        if not str(val).strip():
            val = e.placeholder
        values.append(val)
    if all(str(v).strip() == "" for v in values):
        messagebox.showwarning("Empty Input", "Please fill in at least one field.")
        return
    values += [""] * len_output
    display_values = [""] + values
    tree_frame.insert("", "end", values=display_values)
    clear_fields()
    for e in entry_list:
        e.reset()
    update_row_numbers()


# Edit the selected rows with values from input fields
def edit_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select at least one row to edit.")
        return
    new_values = []
    for e in entry_list:
        val = e.get()
        if not str(val).strip():
            val = e.placeholder
        new_values.append(val)
    new_values += [""] * len_output
    for item in selected:
        current_values = list(tree_frame.item(item, "values"))
        row_number = current_values[0] if current_values else ""
        updated_values = [row_number] + new_values
        tree_frame.item(item, values=updated_values)
    clear_fields()
    for e in entry_list:
        e.reset()


# Delete the selected rows
def delete_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select one or more rows to delete.")
        return
    for item in selected:
        tree_frame.delete(item)
    update_row_numbers()


# Clear all input fields
def clear_fields():
    for e in entry_list:
        e.delete(0, "end")
        e.reset()


# Clear fields from button action (ensures focus is reset)
def clear_fields_button():
    root.focus_set()
    for e in entry_list:
        e.delete(0, "end")
        e.reset()


# Clear outputs in the selected rows
def clear_outputs_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select one or more rows to clear outputs.")
        return
    num_outputs = len(output_list)
    num_columns = len(bottom_list) + num_outputs + 1
    output_start = num_columns - num_outputs
    for item in selected:
        values = list(tree_frame.item(item, "values"))
        for i in range(output_start, num_columns):
            values[i] = ""
        tree_frame.item(item, values=values)


# Select all rows
def select_all():
    tree_frame.selection_set(tree_frame.get_children())


# Deselect all rows
def deselect_all():
    for item in tree_frame.selection():
        tree_frame.selection_remove(item)


# Copy selected row's values into the input fields
def copy_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select a row to copy.")
        return
    values = tree_frame.item(selected[0], "values")
    input_values = values[1:len(entry_list) + 1]
    for i, e in enumerate(entry_list):
        value = input_values[i] if i < len(input_values) else ""
        if value in ("", None):
            e.reset()
        else:
            e.set_value(value)


# Set default values for the input fields
def set_defaults():
    window = tk.Toplevel()
    window.title("Set Default Values")
    window.grab_set()
    tk.Label(window, text="How do you want to set the default values?", font=("Arial", 11)).pack(pady=10)
    def read_from_input_and_close():
        window.destroy()
        read_defaults_from_input()
    def read_from_file_and_close():
        window.destroy()
        read_defaults_from_file()
    def cancel_and_close():
        window.destroy()
    tk.Button(window, text="Read from input fields", width=30, command=read_from_input_and_close).pack(pady=5)
    tk.Button(window, text="Load from file", width=30, command=read_from_file_and_close).pack(pady=5)
    tk.Button(window, text="Cancel", width=30, command=cancel_and_close).pack(pady=10)
    window.update_idletasks()
    w = window.winfo_screenwidth()
    h = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = w // 2 - size[0] // 2
    y = h // 2 - size[1] // 2
    window.geometry(f"+{x}+{y}")


# Read default values from the input fields
def read_defaults_from_input():
    new_defaults = []
    invalid_fields = []
    for i, entry in enumerate(entry_list):
        value = entry.get().strip()
        if value == "":
            new_defaults.append("")
        else:
            try:
                num = int(value)
                if num < 0:
                    raise ValueError
                new_defaults.append(str(num))
            except ValueError:
                new_defaults.append("")
                invalid_fields.append(top_list[i])
    if invalid_fields:
        message = (
            "The following fields contain invalid (non-numeric or negative) values:\n\n" +
            ", ".join(invalid_fields) +
            "\n\nDo you want to continue and set these to empty?"
        )
        proceed = messagebox.askyesno("Invalid Inputs", message)
        if not proceed:
            return
    apply_new_defaults(new_defaults)


# Read default values from a file
def read_defaults_from_file():
    file_path = filedialog.askopenfilename(
        title="Select Default Values File",
        filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    )
    if not file_path:
        return
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("File Read Error", f"An error occurred while reading the file:\n{e}")
        return
    if df.shape[0] == 0:
        messagebox.showerror("Empty File", "The selected file does not contain any rows.")
        return
    if df.shape[0] > 1:
        messagebox.showwarning("Multiple Rows", "The file contains multiple rows: only the first one will be used.")
    first_row = df.iloc[0].to_dict()
    new_defaults = []
    invalid_columns = []
    for col in bottom_list:
        raw_value = first_row.get(col, "")
        value = str(raw_value).strip()
        if value == "":
            new_defaults.append("")
        else:
            try:
                num = int(float(value))
                if num < 0:
                    raise ValueError
                new_defaults.append(str(num))
            except ValueError:
                new_defaults.append("")
                invalid_columns.append(col)

    if invalid_columns:
        message = (
            "The following fields contain invalid (non-numeric or negative) values:\n\n" +
            ", ".join(invalid_columns) +
            "\n\nDo you want to continue and set these to empty?"
        )
        proceed = messagebox.askyesno("Invalid Values", message)
        if not proceed:
            return
    apply_new_defaults(new_defaults)


# Apply new default values
def apply_new_defaults(new_defaults):
    for i, entry in enumerate(entry_list):
        entry.placeholder = new_defaults[i]
        entry.delete(0, tk.END)
        entry._put_placeholder()
    global default_values
    default_values = np.array(new_defaults)
    save = messagebox.askyesno("Save Defaults", "Do you want to save the new default values to a file?")
    if not save:
        return
    filetypes = [("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=filetypes,
        title="Save Default Values"
    )
    if not save_path:
        return
    try:
        df = pd.DataFrame([new_defaults], columns=bottom_list)
        if save_path.endswith(".csv"):
            df.to_csv(save_path, index=False)
        else:
            df.to_excel(save_path, index=False)
        messagebox.showinfo("Save Completed", f"Default values were saved to:\n{os.path.basename(save_path)}")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save default values:\n{e}")


# Clean selected rows (remove invalid values)
def clean_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select at least one row to clean.")
        return
    deleted_count = 0
    num_inputs = len(bottom_list)
    for item in selected:
        values = list(tree_frame.item(item, "values"))
        cleaned_values = values.copy()
        for i in range(1, num_inputs + 1):
            value = values[i].strip()
            if value == "":
                cleaned_values[i] = ""
                continue
            try:
                num = float(value)
                if num >= 0:
                    cleaned_values[i] = str(int(round(num)))
                else:
                    cleaned_values[i] = ""
            except ValueError:
                cleaned_values[i] = ""
        if all(cleaned_values[i] == "" for i in range(1, num_inputs + 1)):
            tree_frame.delete(item)
            deleted_count += 1
        else:
            tree_frame.item(item, values=cleaned_values)
    if deleted_count > 0:
        messagebox.showinfo(
            "Clean Complete",
            f"{deleted_count} row(s) were removed because they had no valid input values after cleaning."
        )
    update_row_numbers()


# Correct selected rows (replace invalids with defaults)
def correct_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select at least one row to correct.")
        return
    deleted_count = 0
    num_inputs = len(bottom_list)
    for item in selected:
        values = list(tree_frame.item(item, "values"))
        all_invalid = True
        for i in range(1, num_inputs + 1):
            val = values[i].strip()
            try:
                num = float(val)
                if num >= 0:
                    all_invalid = False
                    break
            except ValueError:
                continue
        if all_invalid:
            tree_frame.delete(item)
            deleted_count += 1
            continue
        corrected_values = values.copy()
        for i in range(1, num_inputs + 1):
            val = values[i].strip()
            entry_index = i - 1
            try:
                num = float(val)
                if num >= 0:
                    corrected_values[i] = str(int(round(num)))
                else:
                    corrected_values[i] = entry_list[entry_index].placeholder
            except ValueError:
                corrected_values[i] = entry_list[entry_index].placeholder
        tree_frame.item(item, values=corrected_values)
    if deleted_count > 0:
        messagebox.showinfo(
            "Correction Complete",
            f"{deleted_count} row(s) were removed because they contained only invalid input values."
        )
    update_row_numbers()


# Calculate the outputs for the selected rows
def calculate_selected():
    selected = tree_frame.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select at least one row to calculate.")
        return
    failed_rows = []
    for item in selected:
        values = list(tree_frame.item(item, "values"))
        inputs = values[1:1 + len(entry_list)]
        output_val, output_flag, missing = compute_outputs(inputs, column_names=bottom_list)
        filtered_missing = [col for col in missing if col != "threshold"]
        updated_values = [values[0]] + inputs + [output_val, output_flag]
        tree_frame.item(item, values=updated_values)
        if filtered_missing and not output_val:
            failed_rows.append({
                "row": tree_frame.index(item) + 1,
                "missing": filtered_missing
            })
    if failed_rows:
        count = len(failed_rows)
        short_msg = (
            f"Calculation could not be performed for {count} row(s).\n\n"
            "Please correct the inputs manually or use the 'Correct' function."
        )
        messagebox.showwarning("Invalid Input", short_msg)
        if messagebox.askyesno("Show Details?", "Do you want to see which rows failed?"):
            detailed_msg = ""
            for row_info in failed_rows:
                detailed_msg += f"Row {row_info['row']}: missing or invalid → {', '.join(row_info['missing'])}\n"
            show_scrollable_warning("Error Details", detailed_msg.strip())


# Show a scrollable warning popup with a title and message
def show_scrollable_warning(title, message):
    popup = Toplevel()
    popup.title(title)
    popup.geometry("600x400")
    popup.grab_set()
    text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Arial", 10))
    text_area.insert(tk.END, message)
    text_area.configure(state="disabled")
    text_area.pack(expand=True, fill="both", padx=10, pady=10)
    Button(popup, text="OK", command=popup.destroy).pack(pady=(0, 10))    


# Function to deselect all rows in the Treeview when clicking outside
def click_anywhere(event):
    widget = event.widget
    allowed_widgets = (tk.Entry, tk.Button, tk.Menubutton, ttk.Entry, ttk.Button, ttk.Combobox, tk.Label, tk.Frame)
    if isinstance(widget, allowed_widgets):
        return
    if widget == tree_frame:
        region = tree_frame.identify("region", event.x, event.y)
        if region != "cell":
            deselect_all()
    else:
        deselect_all()


# Function to open the README file in a new window
def open_readme():
    try:
        with open(resource_path("README.txt"), "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        messagebox.showerror("Error", "The README.txt file was not found.")
        return
    readme_window = tk.Toplevel()
    readme_window.title("README")
    readme_window.geometry("600x400")
    container = tk.Frame(readme_window)
    container.pack(fill="both", expand=True)
    text_widget = tk.Text(container, wrap="none")
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")
    text_widget.grid(row=0, column=0, sticky="nsew")
    y_scroll = tk.Scrollbar(container, orient="vertical", command=text_widget.yview)
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll = tk.Scrollbar(container, orient="horizontal", command=text_widget.xview)
    x_scroll.grid(row=1, column=0, sticky="ew")
    text_widget.config(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)


# Function to update the scrollbars based on the scroll frame's view
def update_scrollbars(scroll_frame, x_scroll=None, y_scroll=None, event=None):
    if y_scroll is not None:
        if scroll_frame.yview() == (0.0, 1.0):
            y_scroll.grid_remove()
        else:
            y_scroll.grid()
    if x_scroll is not None:
        if scroll_frame.xview() == (0.0, 1.0):
            x_scroll.grid_remove()
        else:
            x_scroll.grid()


# Function to trigger the scrollbars to update based on the scroll frame's view
def trigger_scrollbars(scroll_frame, event=None):
    scroll_frame.bind("<Configure>", update_scrollbars(scroll_frame))
    scroll_frame.bind("<KeyRelease>", update_scrollbars(scroll_frame))
    scroll_frame.bind("<MouseWheel>", update_scrollbars(scroll_frame))


# Function to update the scroll region of the canvas when the window is resized
def update_scrollregion(event):
    canvas.itemconfig(canvas_window, height=event.height)
    canvas.configure(scrollregion=canvas.bbox("all"))


# Function to create an example file with default values
def print_example_file(filetype="xlsx"):
    data = {}
    for col, default in zip(bottom_list, default_list):
        data.update({col: [default, default, default]})
        df = pd.DataFrame(data)
    filename = f"example_data.{filetype}"
    filepath = os.path.join(os.getcwd(), filename)
    try:
        if filetype == "csv":
            df.to_csv(filepath, index=False)
        elif filetype == "xlsx":
            df.to_excel(filepath, index=False)                
        messagebox.showinfo("Success", f"File saved as:\n{filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{str(e)}")


# Function to exit the application with a confirmation dialog
def exit_app():
    if messagebox.askokcancel("Exit", "Do you really want to exit?"):
        root.destroy()


# Function to export the entire dataset to a file
def export_file(tree, only_inputs=False):
    items = tree.get_children()
    if not items:
        messagebox.showinfo("No data", "There is no data to export.")
        return
    cols = bottom_list if only_inputs else total_list
    cols = cols.copy()
    if cols[0].lower() == "row" or cols[0].lower() == "#" or cols[0].startswith("Riga"):
        cols = cols[1:]
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
        title="Save entire dataset"
    )
    if not file_path:
        return
    data = []
    for row_id in items:
        values = tree.item(row_id)["values"][1:]
        row = [values[i] if i < len(values) else "" for i in range(len(cols))]
        data.append(row)
    try:
        if file_path.endswith(".csv"):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(data)
        elif file_path.endswith(".xlsx"):
            df = pd.DataFrame(data, columns=cols)
            df.to_excel(file_path, index=False)
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return
        messagebox.showinfo("Success", f"File saved to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


# Function to export only the selected rows to a file
def export_selected(selected_only=False, only_inputs=False):
    items = tree_frame.selection() if selected_only else tree_frame.get_children()
    if not items:
        messagebox.showinfo("No selection", "Please select one or more rows to export.")
        return
    cols = bottom_list if only_inputs else total_list
    cols = cols.copy()
    if cols[0].lower() == "row" or cols[0].lower() == "#" or cols[0].startswith("Riga"):
        cols = cols[1:]
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
        title="Save selected rows"
    )
    if not file_path:
        return
    ext = os.path.splitext(file_path)[1].lower()
    data = []
    for item in items:
        values = tree_frame.item(item, "values")[1:]
        row = [values[i] if i < len(values) else "" for i in range(len(cols))]
        data.append(row)
    try:
        if ext == ".csv":
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(data)
        elif ext == ".xlsx":
            df = pd.DataFrame(data, columns=cols)
            df.to_excel(file_path, index=False)
        else:
            messagebox.showerror("Unsupported Format", "Only CSV and Excel files are supported.")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")
        return
    messagebox.showinfo("Exported", f"Data exported to:\n{file_path}")


# Function to import a file and populate the Treeview with its data
def import_file(tree, input_columns=bottom_list, output_columns=output_list):
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
        title="Open dataset file"
    )
    if not file_path:
        return
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return
        df = df.fillna("")
        df.columns = [c.strip() for c in df.columns]
        file_columns = df.columns.tolist()
        input_columns_clean = [col.strip() for col in input_columns]
        output_columns_clean = [col.strip() for col in output_columns]
        found_inputs = [col for col in input_columns_clean if col in file_columns]
        found_outputs = [col for col in output_columns_clean if col in file_columns]
        if not found_inputs:
            messagebox.showerror("Missing Inputs", "No valid input columns found in the file.")
            return
        import_outputs = False
        if found_outputs:
            import_outputs = messagebox.askyesno("Import outputs?", "Output columns found in the file. Import them?")
        import_columns = found_inputs + (found_outputs if import_outputs else [])
        imported_rows = 0
        for _, row in df.iterrows():
            if not any(str(row.get(col, "")).strip() for col in found_inputs):
                continue
            values = [""]
            for col in input_columns:
                values.append(str(row.get(col, "")).strip() if col in import_columns else "")
            for col in output_columns:
                values.append(str(row.get(col, "")).strip() if import_outputs and col in import_columns else "")
            tree.insert("", "end", values=values)
            imported_rows += 1
        if imported_rows == 0:
            messagebox.showinfo("No Data Imported", "No valid rows were found with non-empty input fields.")
            return
        missing_inputs = [col for col in input_columns_clean if col not in file_columns]
        missing_outputs = [col for col in output_columns_clean if col not in file_columns] if import_outputs else []
        msg = f"{imported_rows} row(s) successfully imported."
        if missing_inputs or missing_outputs:
            msg += "\n\nSome expected columns were not found:\n"
            if missing_inputs:
                msg += f" - Missing input columns: {', '.join(missing_inputs)}\n"
            if missing_outputs:
                msg += f" - Missing output columns: {', '.join(missing_outputs)}"
        messagebox.showinfo("Import Completed", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    update_row_numbers()





# Root configuration, make root expandable
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main frame with grid layout
main_frame = tk.Frame(root, bg="lightgray")
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Canvas with horizontal scrollbar
canvas = tk.Canvas(main_frame)
canvas.grid(row=0, column=0, rowspan=3, sticky="nsew")
x_scroll = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
x_scroll.grid(row=1, column=0, sticky="ew")
canvas.config(xscrollcommand=lambda *args: (x_scroll.set(*args), update_scrollbars(canvas, x_scroll=x_scroll)))
canvas.grid(row=0, column=0, sticky="nsew")
x_scroll.grid(row=1, column=0, sticky="ew")
trigger_scrollbars(canvas)

# Scrollable frame inside the canvas
scrollable_frame = tk.Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.bind("<Configure>", update_scrollregion)


# Buttons configuration
buttonrow = 0
buttonpady = 5
buttonpadx = 5
button_frame = tk.Frame(scrollable_frame)
button_frame.pack(fill="x", pady=5)
buttons = ["Add", "Copy", "Edit", "Set Defaults", "Clear Inputs", "Clear Outputs", "Clean", "Correct", "Select All", "Deselect All", "Delete"]
commands = [add_row, copy_selected, edit_selected, set_defaults, clear_fields_button, clear_outputs_selected, clean_selected, correct_selected, select_all, deselect_all, delete_selected]
for i, (name, command) in enumerate(zip(buttons, commands)):
    bottone = tk.Button(button_frame, text=name, command=lambda cmd=command: cmd())
    bottone.grid(row=buttonrow, column=i, padx=buttonpadx, pady=buttonpady, sticky="w")
    Tooltip(bottone, button_tooltips.get(name, ""))
default_font = tkFont.nametofont(tk.Button(root).cget("font")).copy()
default_font.configure(size=10, weight="bold")
runner = tk.Button(button_frame, text="▶️ Run Calculation", command=lambda: calculate_selected(), bg="#ffcc00", fg="black", font=default_font)
runner.grid(row=buttonrow, column=i+1, padx=buttonpadx*5, pady=buttonpady, sticky="w")
Tooltip(runner, button_tooltips["▶️ Run Calculation"])


# Input fields
input_frame = tk.Frame(scrollable_frame)
input_frame.pack(fill="x", pady=5)
max_widths = []
for element in range(len_list):
    feature_code = bottom_list[element]
    feature_name = top_list[element]
    description = explanations.get(feature_code, "No description available.")
    top_label = tk.Label(input_frame, text=top_list[element], font=font)
    top_label.grid(row=0, column=element, padx=2, pady=(5, 2))
    all_scalable_widgets.append(top_label)
    entry_list[element] = EntryWithPlaceholder(input_frame, placeholder=default_list[element], width=14, font=font)
    entry_list[element].grid(row=1, column=element, padx=3, pady=(2, 5), sticky="ew")
    all_scalable_widgets.append(entry_list[element])
    Tooltip(top_label, f"{description} ➔ {feature_code}")
    Tooltip(entry_list[element], f'Default value for "{feature_code}".\nYou can enter a different value.')


# Treeview (Table)
table_frame = tk.Frame(scrollable_frame)
table_frame.pack(fill="both", expand=True, pady=5)
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)
columns = [f"C{i+1}" for i in range(len(total_list_index))]
tree_frame = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
for i, label in enumerate(total_list_index):
    tree_frame.heading(f"C{i+1}", text=label)
    tree_frame.column(f"C{i+1}", width=80, anchor="center")
tree_frame.grid(row=0, column=0, sticky="nsew")
y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree_frame.yview)
y_scroll.grid(row=0, column=1, sticky="ns")
tree_frame.config(yscrollcommand=lambda *args: (y_scroll.set(*args), update_scrollbars(tree_frame, y_scroll=y_scroll)))
trigger_scrollbars(tree_frame)
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)


# Menu bar
menu_bar = tk.Menu(root)
# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Import Dataset", command=lambda: import_file(tree_frame, bottom_list))
# Export the whole dataset - submenu
export_dataset_submenu = tk.Menu(file_menu, tearoff=0)
export_dataset_submenu.add_command(label="All Data", command=lambda: export_file(tree_frame, only_inputs=False))
export_dataset_submenu.add_command(label="Only Inputs", command=lambda: export_file(tree_frame, only_inputs=True))
file_menu.add_cascade(label="Export Dataset", menu=export_dataset_submenu)
# Export only the selected rows - submenu
export_selected_submenu = tk.Menu(file_menu, tearoff=0)
export_selected_submenu.add_command(label="All Data", command=lambda: export_selected(selected_only=True, only_inputs=False))
export_selected_submenu.add_command(label="Only Inputs", command=lambda: export_selected(selected_only=True, only_inputs=True))
file_menu.add_cascade(label="Export Selected", menu=export_selected_submenu)
# Print example file - submenu
print_example_submenu = tk.Menu(file_menu, tearoff=0)
print_example_submenu.add_command(label="As Excel", command=lambda: print_example_file("xlsx"))
print_example_submenu.add_command(label="As CSV", command=lambda: print_example_file("csv"))
file_menu.add_cascade(label="Print Example", menu=print_example_submenu)
# Add a separator and exit
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)
menu_bar.add_cascade(label="File", menu=file_menu)
# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Open README", command=open_readme)
menu_bar.add_cascade(label="Help", menu=help_menu)
# Assign menu to window
root.config(menu=menu_bar)


# Bindings
root.bind("<Button-1>", click_anywhere)  # Deselect treeview items on click


for entry in entry_list:
    entry.bind("<Return>", lambda event: add_row())


# Run the main loop
root.mainloop()
