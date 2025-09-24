# Utility functions for the GUI app

import tkinter as tk
import pandas as pd
import joblib
import os
import sys
from tkinter import font as tkfont


# Entry widget with placeholder support
class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg'] if 'fg' in kwargs else 'black'
        self.has_placeholder = False
        current_font = tkfont.nametofont(self['font'])
        self.normal_font = current_font.copy()
        self.bold_font = current_font.copy()
        self.bold_font.configure(weight='bold')
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self._put_placeholder()
    def _put_placeholder(self):
        self.delete(0, 'end')
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        self['font'] = self.normal_font
        self.has_placeholder = True
    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color
            self['font'] = self.bold_font
            self.has_placeholder = False
    def _on_focus_out(self, event):
        if not self.get():
            self._put_placeholder()
    def get_value_or_placeholder(self):
        if self.has_placeholder or not self.get().strip():
            return self.placeholder
        return self.get()
    def reset(self):
        if not self.focus_get() == self:
            self._put_placeholder()
    def set_value(self, value):
        self.delete(0, 'end')
        if value in ("", None):
            self._put_placeholder()
        else:
            self.insert(0, value)
            self['fg'] = self.default_fg_color
            self['font'] = self.bold_font
            self.has_placeholder = False


# Tooltip class for widgets
class Tooltip:
    def __init__(self, widget, text, wraplength=300, timeout=4000):
        self.widget = widget
        self.text = text
        self.wraplength = wraplength
        self.timeout = timeout
        self.tipwindow = None
        self.close_id = None
        self.root = widget.winfo_toplevel()
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        label = tk.Label(
            tw, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("TkDefaultFont", 9), wraplength=self.wraplength
        )
        label.pack(ipadx=4, ipady=2)
        tw.update_idletasks()
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_h = self.widget.winfo_height()
        tip_w = tw.winfo_width()
        tip_h = tw.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        x = widget_x + 20
        y = widget_y + widget_h + 10
        if x + tip_w > root_x + root_w:
            x = root_x + root_w - tip_w - 10
        if y + tip_h > root_y + root_h:
            y = widget_y - tip_h - 10
        if x < root_x:
            x = root_x + 10
        if y < root_y:
            y = root_y + 10
        tw.wm_geometry(f"+{x}+{y}")
        self.close_id = tw.after(self.timeout, self.hide_tip)
    def hide_tip(self, event=None):
        if self.tipwindow:
            if self.close_id:
                self.tipwindow.after_cancel(self.close_id)
                self.close_id = None
            self.tipwindow.destroy()
            self.tipwindow = None


# Return absolute path of a resource file
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Compute outputs using a saved model
def compute_outputs(inputs, column_names=None,
                    model_path=resource_path("model.pkl"),
                    norm_params_path=resource_path("normalization_params.csv")):
    num_inputs = len(inputs)
    if num_inputs < 2:
        return "", "ERR", column_names or ["input"]
    threshold_str = inputs[-1]
    input_strs = inputs[:-1]
    input_cols = column_names[:-1] if column_names else [f"Input{i+1}" for i in range(num_inputs - 1)]
    valid_values = []
    missing_fields = []
    for i, val in enumerate(input_strs):
        try:
            valid_values.append(float(val))
        except:
            missing_fields.append(input_cols[i])
    try:
        threshold = float(threshold_str)
        threshold_valid = True
    except:
        threshold_valid = False
        if column_names:
            missing_fields.append(column_names[-1])
        else:
            missing_fields.append(f"Input{num_inputs}")
    if len(valid_values) != len(input_strs):
        return "", "ERR", missing_fields
    input_df = pd.DataFrame([valid_values], columns=input_cols)
    norm_params = pd.read_csv(norm_params_path, index_col=0)
    min_vals = norm_params["min"]
    max_vals = norm_params["max"]
    input_df = (input_df - min_vals) / (max_vals - min_vals)
    input_df = input_df.clip(0, 1)
    try:
        model = joblib.load(model_path)
        pred = model.predict(input_df)[0]
        output_val = str(int(round(pred)))
    except Exception as e:
        return "", "ERR", ["ModelError: " + str(e)]
    if threshold_valid:
        output_flag = "OK" if pred < threshold else "HIGH"
    else:
        output_flag = "ERR"
    return output_val, output_flag, missing_fields
