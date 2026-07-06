import sqlite3
import tkinter as tk
from tkinter import ttk

# Connect to database
conn = sqlite3.connect("expenses.db")
cur = conn.cursor()

# ---------- Function to create Users Window ----------
def show_users():
    users_win = tk.Toplevel()
    users_win.title("Users Table")

    users_label = ttk.Label(users_win, text="Users Table", font=("Helvetica", 14, "bold"))
    users_label.pack(pady=5)

    users_tree = ttk.Treeview(users_win, columns=("ID", "Name", "Email"), show="headings")
    users_tree.pack(padx=10, pady=5, fill="both", expand=True)

    users_tree.heading("ID", text="ID")
    users_tree.heading("Name", text="Name")
    users_tree.heading("Email", text="Email")

    # Highlight ID column
    style = ttk.Style()
    style.map("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))
    users_tree.tag_configure("highlight", background="#DFF0D8")

    try:
        cur.execute("SELECT * FROM users")
        for row in cur.fetchall():
            users_tree.insert("", "end", values=row, tags=("highlight",))
    except Exception as e:
        users_tree.insert("", "end", values=("Error", str(e), ""))

# ---------- Function to create Expenses Window ----------
def show_expenses():
    expenses_win = tk.Toplevel()
    expenses_win.title("Expenses Table")

    expenses_label = ttk.Label(expenses_win, text="Expenses Table", font=("Helvetica", 14, "bold"))
    expenses_label.pack(pady=5)

    expenses_tree = ttk.Treeview(expenses_win, columns=("ID", "User ID", "Category", "Amount", "Date"), show="headings")
    expenses_tree.pack(padx=10, pady=5, fill="both", expand=True)

    expenses_tree.heading("ID", text="ID")
    expenses_tree.heading("User ID", text="User ID")
    expenses_tree.heading("Category", text="Category")
    expenses_tree.heading("Amount", text="Amount")
    expenses_tree.heading("Date", text="Date")

    # Highlight User ID column
    expenses_tree.tag_configure("highlight", background="#D9EDF7")

    try:
        cur.execute("SELECT * FROM expenses")
        for row in cur.fetchall():
            expenses_tree.insert("", "end", values=row, tags=("highlight",))
    except Exception as e:
        expenses_tree.insert("", "end", values=("Error", "", str(e), "", ""))

# ---------- Treeview Style Fix ----------
def fixed_map(option):
    # Fix for setting style when widget is disabled
    return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

# ---------- Main Window ----------
root = tk.Tk()
root.title("Expense Manager GUI")
root.geometry("300x150")

style = ttk.Style()
style.theme_use("default")

btn1 = ttk.Button(root, text="Show Users Table", command=show_users)
btn1.pack(pady=10)

btn2 = ttk.Button(root, text="Show Expenses Table", command=show_expenses)
btn2.pack(pady=10)

root.mainloop()

# Close DB connection
conn.close()
