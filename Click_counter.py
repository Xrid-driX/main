#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from typing import Counter
from pynput import keyboard
import threading
import time
from tkinter import colorchooser

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, current_value):
        super().__init__(parent)
        self.result = None
        
        # Window setup
        self.title(title)
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Style
        self.configure(bg="#f0f0f0")
        self.style = ttk.Style()
        self.style.configure("Dialog.TLabel", font=("Helvetica", 12), padding=5)
        self.style.configure("Dialog.TEntry", font=("Helvetica", 14))
        self.style.configure("Dialog.TButton", font=("Helvetica", 11), padding=5)
        
        # Create widgets
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Enter new value:", 
                 style="Dialog.TLabel").pack(pady=(0, 10))
        
        # Entry with validation
        vcmd = (self.register(self.validate_number), '%P')
        self.entry = ttk.Entry(main_frame, 
                             validate='key', 
                             validatecommand=vcmd,
                             justify="center",
                             font=("Helvetica", 18))
        self.entry.insert(0, str(current_value))
        self.entry.pack(pady=(0, 20), ipady=5)
        self.entry.select_range(0, tk.END)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Cancel", 
                  command=self.cancel, 
                  style="Dialog.TButton").pack(side="left", expand=True, padx=5)
        
        ttk.Button(btn_frame, text="Save", 
                  command=self.save, 
                  style="Dialog.TButton").pack(side="right", expand=True, padx=5)
        
        # Key bindings
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.cancel())
        
        # Focus entry
        self.entry.focus_set()
        
    def validate_number(self, value):
        if value == "": return True
        try:
            int(value)
            return True
        except ValueError:
            return False
            
    def save(self):
        try:
            self.result = int(self.entry.get())
            self.destroy()
        except ValueError:
            messagebox.showwarning("Invalid Input", 
                                 "Please enter a valid number.", 
                                 parent=self)
            
    def cancel(self):
        self.destroy()
class CounterTableView(ttk.Frame):


    def __init__(self, parent, counters):
        super().__init__(parent)
        self.counters = counters
        
        # Create Treeview
        columns = ('name', 'count', 'actions')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('name', text='Counter Name')
        self.tree.heading('count', text='Value')
        self.tree.heading('actions', text='Actions')
        
        # Column widths
        self.tree.column('name', width=150)
        self.tree.column('count', width=100)
        self.tree.column('actions', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.update_table()
        
    def update_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add counters to table
        for counter in self.counters:
            self.tree.insert('', 'end', values=(
                counter.name,
                counter.count,
                'Use Grid View for Actions'
            ))

class CounterWidget(ttk.Frame):
    def __init__(self, parent, name="Counter", initial_value=0, on_delete=None, on_rename=None):
        super().__init__(parent)
        self.parent = parent
        self.name = name
        self.count = initial_value
        self.on_delete = on_delete
        self.on_rename = on_rename
        self.active = False
        self.color = "#FFFFFF"
        self.last_increment_time = 0
        self.increment_delay = 0.2  # 200ms delay between increments
        
        self.style = ttk.Style()
        self.style.configure("Counter.TFrame", background="#1E1E1E", relief="flat", borderwidth=10)
        self.style.configure("CounterButton.TButton", padding=5, relief="flat", background="#333333")
        
        self.create_widgets()

    def increment(self):
        current_time = time.time()
        if current_time - self.last_increment_time >= self.increment_delay:
            self.count += 1
            self.value_label.config(text=str(self.count))
            self.last_increment_time = current_time
        
    def decrement(self):
        if self.count != 0:
            current_time = time.time()
            if current_time - self.last_increment_time >= self.increment_delay:
                self.count -= 1
                self.value_label.config(text=str(self.count))
                self.last_increment_time = current_time

    def edit_value(self):
        dialog = CustomDialog(self, "Edit Counter", self.count)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.count = dialog.result
            self.value_label.config(text=str(self.count))
        
    def reset(self):
        self.count = 0
        self.value_label.config(text="0")
        
    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.name_label.configure(fg=color)
            self.value_label.configure(fg=color)
    
    def rename(self):
        new_name = simpledialog.askstring("Rename Counter", "Enter new name:",
                                        initialvalue=self.name,
                                        parent=self.winfo_toplevel())
        if new_name:
            self.name = new_name
            self.name_label.config(text=self.name)
            if self.on_rename:
                self.on_rename(self)

    def create_widgets(self):
        self.container = tk.Frame(self, bg="#1E1E1E", padx=10, pady=10)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.name_frame = tk.Frame(self.container, bg="#D3D3D3", relief="flat")
        self.name_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.name_label = tk.Label(
            self.name_frame,
            text=self.name,
            font=("Helvetica", 12),
            bg="#D3D3D3",
            fg="#000000"
        )
        self.name_label.pack(pady=5)
        
        self.value_frame = tk.Frame(self.container, bg="#D3D3D3", relief="flat")
        self.value_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.value_label = tk.Label(
            self.value_frame,
            text=str(self.count),
            font=("Helvetica", 24),
            bg="#D3D3D3",
            fg="#000000"
        )
        self.value_label.pack(pady=10)
        
        button_frame = tk.Frame(self.container, bg="#1E1E1E")
        button_frame.pack(fill=tk.X)
        
        button_style = {
            'bg': '#333333',
            'fg': 'white',
            'relief': 'flat',
            'width': 8,
            'pady': 5
        }

        # Action Buttons

        buttons = [
            ("+1", self.increment),
            ("-1", self.decrement),
            ("reset", self.reset),
            ("edit", self.edit_value),
            ("rename", self.rename),
            ("color", self.choose_color),
            ("delete", lambda c=self: self.on_delete(c))
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command, **button_style).pack(side=tk.LEFT, padx=2)

    def set_active(self, active):
        self.active = active
        border_color = "#4a90e2" if active else "#1E1E1E"
        self.container.configure(highlightbackground=border_color, highlightthickness=2)


class ClickCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Counter Application")
        self.root.geometry("800x600")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("BigLabel.TLabel", font=("Helvetica", 24))
        self.style.configure("TButton", padding=2)
        
        self.counters = []
        self.active_counter_index = 0
        self.COLUMNS = 3
        
        self.is_paused = False
        self.enter_enabled = True
        self.keyboard_listener = None
        
        # Autosave configuration
        self.autosave_interval = 60  # 1 minute in seconds
        self.last_autosave = time.time()
        
        self.create_widgets()  # Properly calls the method
        self.load_state()
        
        # Start the keyboard listener thread
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()
        
        # Start autosave
        self.start_autosave()

    def start_autosave(self):
        """Start the autosave timer"""
        self.check_autosave()
        
    def check_autosave(self):
        """Check if it's time to autosave and schedule the next check"""
        current_time = time.time()
        if current_time - self.last_autosave >= self.autosave_interval:
            self.save_to_file(autosave=True)
            self.last_autosave = current_time
        
        # Schedule the next check
        self.root.after(60000, self.check_autosave)  # Check every minute
    
    def start_listener(self):
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            self.keyboard_listener = listener
            listener.join()

    def on_key_press(self, key):
        if self.is_paused:
            return
        
        try:
            if key == keyboard.Key.shift:
                self.toggle_enter_key()
            elif key == keyboard.Key.enter and self.enter_enabled:
                self.increment_active()
            elif key == keyboard.Key.up:
                self.increment_active()
            elif key == keyboard.Key.down:
                self.decrement_active()
            elif hasattr(key, 'char') and key.char == '`':
                self.reset_active()
        except AttributeError:
            pass

    def toggle_enter_key(self):
        self.enter_enabled = not self.enter_enabled
        status = "enabled" if self.enter_enabled else "disabled"
        self.status_label.config(text=f"Enter key is now {status}.")

    def pause_shortcuts(self):
        self.is_paused = True
        self.status_label.config(text="App is paused.")

    def resume_shortcuts(self):
        self.is_paused = False
        self.status_label.config(text="App is running.")

    def increment_active(self):
        if self.counters:
            self.counters[self.active_counter_index].increment()
            self.table_view.update_table()

    def decrement_active(self):
        if self.counters:
            self.counters[self.active_counter_index].decrement()
            self.table_view.update_table()

    def reset_active(self):
        if self.counters:
            self.counters[self.active_counter_index].reset()
            self.table_view.update_table()

    def add_counter(self, name="Counter", initial_value=0):
        counter = CounterWidget(self.grid_frame, name, initial_value, 
                                on_delete=self.delete_counter, 
                                on_rename=self.update_table_view)
        counter.grid(row=len(self.counters), column=0, padx=5, pady=5, sticky="ew")  # Changed to single column
        self.counters.append(counter)
        self.table_view.update_table()

    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Grid View Tab
        self.grid_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.grid_tab, text="Grid View")
        
        # Table View Tab
        self.table_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="Table View")
        
        # Setup Grid View
        self.setup_grid_view()
        
        # Setup Table View
        self.table_view = CounterTableView(self.table_tab, self.counters)
        self.table_view.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Status Label
        self.status_label = ttk.Label(self.root, text="App is running.", 
                                      font=("Helvetica", 12, "italic"))
        self.status_label.pack(pady=5)
        
        # Control frame for buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=5)
        
        # Add buttons
        for btn_text, cmd in [
            ("Toggle Enter Key", self.toggle_enter_key),
            ("Pause Shortcuts", self.pause_shortcuts),
            ("Resume Shortcuts", self.resume_shortcuts)
        ]:
            ttk.Button(control_frame, text=btn_text, command=cmd).pack(
                side="left", padx=5)
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def setup_grid_view(self):
        # Main container for grid view
        self.main_frame = ttk.Frame(self.grid_tab, padding="10")
        self.main_frame.pack(expand=True, fill="both")
        
        # Control buttons at top
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill="x", pady=5)
        
        ttk.Button(control_frame, text="Add Counter", 
                   command=self.add_counter).pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Save to File", 
                   command=lambda: self.save_to_file(False)).pack(side="left", padx=5)
        
        # Instructions label
        ttk.Label(control_frame, 
                  text="Keyboard up: +1 | Keyboard Down: -1 | Keyboard ` : Reset | Autosave every 1 minute", 
                  font=("Helvetica", 10)).pack(side="right", padx=5)

        # Scrollable frame
        self.canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", 
                                  command=self.canvas.yview)
        
        self.grid_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.grid_frame.bind("<Configure>", 
                             lambda e: self.canvas.configure(
                                 scrollregion=self.canvas.bbox("all")))

    def delete_counter(self, counter):
        if counter in self.counters:
            self.counters.remove(counter)
            counter.destroy()
            self.table_view.update_table()

    def update_table_view(self, counter=None):
        self.table_view.update_table()

    def save_to_file(self, autosave=False):
        data = [{'name': counter.name, 'count': counter.count} 
                for counter in self.counters]
        try:
            with open('counters.json', 'w') as f:
                json.dump(data, f)
            if not autosave:
                messagebox.showinfo("Success", "Counters saved successfully!")
            else:
                self.status_label.config(text="Autosaved successfully.")
                self.root.after(3000, lambda: self.status_label.config(
                    text="App is running."))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save counters: {str(e)}")

    def load_state(self):
        try:
            with open('counters.json', 'r') as f:
                data = json.load(f)
                for counter_data in data:
                    self.add_counter(counter_data['name'], counter_data['count'])
        except FileNotFoundError:
            pass

    def on_tab_change(self, event):
        self.table_view.update_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClickCounter(root)
    root.mainloop()
