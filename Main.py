import sqlite3
import csv
import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from datetime import datetime

class SmartExpenseManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Manager")
        self.root.geometry("900x650")
        self.root.configure(bg="white")
        self.theme = "light"
        self.user = None
        self.budget = 0

        self.db_connect()
        self.build_login_screen()

    def db_connect(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT,
                            amount REAL,
                            category TEXT,
                            date TEXT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
                            username TEXT PRIMARY KEY,
                            password TEXT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS budgets (
                            username TEXT PRIMARY KEY,
                            budget REAL)""")
        self.conn.commit()

    def switch_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.build_dashboard()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_login_screen(self):
        self.clear_screen()
        self.root.configure(bg="white")
        Label(self.root, text="Smart Expense Manager", font=("Arial", 22, "bold"), bg="white").pack(pady=30)

        frame = Frame(self.root, bg="white")
        frame.pack()

        Label(frame, text="Username:", font=("Arial", 14), bg="white").grid(row=0, column=0, pady=10, sticky="e")
        self.username_entry = Entry(frame, font=("Arial", 14), width=25)
        self.username_entry.grid(row=0, column=1, padx=10)

        Label(frame, text="Password:", font=("Arial", 14), bg="white").grid(row=1, column=0, pady=10, sticky="e")
        self.password_entry = Entry(frame, show="*", font=("Arial", 14), width=25)
        self.password_entry.grid(row=1, column=1, padx=10)

        Button(frame, text="Login", font=("Arial", 12), width=12, command=self.login).grid(row=2, column=0, pady=20)
        Button(frame, text="Register", font=("Arial", 12), width=12, command=self.register).grid(row=2, column=1, pady=20)

    def login(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        self.cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = self.cur.fetchone()
        if result:
            self.user = user
            self.cur.execute("SELECT budget FROM budgets WHERE username=?", (self.user,))
            b = self.cur.fetchone()
            self.budget = b[0] if b else 0
            self.build_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def register(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        try:
            self.cur.execute("INSERT INTO users VALUES (?, ?)", (user, pwd))
            self.conn.commit()
            messagebox.showinfo("Registered", "Registration successful. Please log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def build_dashboard(self):
        self.clear_screen()
        bg_color = "#2e2e2e" if self.theme == "dark" else "white"
        fg_color = "white" if self.theme == "dark" else "black"
        entry_bg = "#444" if self.theme == "dark" else "white"
        self.root.configure(bg=bg_color)

        top_frame = Frame(self.root, bg=bg_color)
        top_frame.pack(fill=X, pady=10)

        Label(top_frame, text=f"Welcome, {self.user}", font=("Arial", 16), bg=bg_color, fg=fg_color).pack(side=LEFT, padx=20)
        Button(top_frame, text="Logout", command=self.build_login_screen).pack(side=RIGHT, padx=10)
        Button(top_frame, text="Toggle Theme", command=self.switch_theme).pack(side=RIGHT)

        form_frame = Frame(self.root, bg=bg_color)
        form_frame.pack(pady=10)

        Label(form_frame, text="Amount (₹):", font=("Arial", 12), bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = Entry(form_frame, font=("Arial", 12), bg=entry_bg, fg=fg_color)
        self.amount_entry.grid(row=0, column=1, padx=5)

        Label(form_frame, text="Category:", font=("Arial", 12), bg=bg_color, fg=fg_color).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_entry = Entry(form_frame, font=("Arial", 12), bg=entry_bg, fg=fg_color)
        self.category_entry.grid(row=1, column=1, padx=5)

        Label(form_frame, text="Date:", font=("Arial", 12), bg=bg_color, fg=fg_color).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = DateEntry(form_frame, font=("Arial", 12), width=19)
        self.date_entry.grid(row=2, column=1, padx=5)

        Button(form_frame, text="Add Expense", font=("Arial", 12), command=self.add_expense).grid(row=3, columnspan=2, pady=10)

        filter_frame = Frame(self.root, bg=bg_color)
        filter_frame.pack(pady=5)

        Label(filter_frame, text="Filter Category:", bg=bg_color, fg=fg_color).grid(row=0, column=0)
        self.filter_category = Entry(filter_frame, width=15)
        self.filter_category.grid(row=0, column=1, padx=5)

        Label(filter_frame, text="Start Date:", bg=bg_color, fg=fg_color).grid(row=0, column=2)
        self.filter_start = DateEntry(filter_frame, width=12)
        self.filter_start.grid(row=0, column=3, padx=5)

        Label(filter_frame, text="End Date:", bg=bg_color, fg=fg_color).grid(row=0, column=4)
        self.filter_end = DateEntry(filter_frame, width=12)
        self.filter_end.grid(row=0, column=5, padx=5)

        Button(filter_frame, text="Apply Filter", command=self.apply_filter).grid(row=0, column=6, padx=5)
        Button(filter_frame, text="Clear Filter", command=self.show_expenses).grid(row=0, column=7, padx=5)

        action_frame = Frame(self.root, bg=bg_color)
        action_frame.pack(pady=10)

        Button(action_frame, text="Export to CSV", command=self.export_to_csv).pack(side=LEFT, padx=10)
        Button(action_frame, text="Show Charts", command=self.show_charts).pack(side=LEFT, padx=10)
        Button(action_frame, text="Set Budget", command=self.set_budget_popup).pack(side=LEFT, padx=10)

        self.table_frame = Frame(self.root)
        self.table_frame.pack(pady=10, fill=BOTH, expand=True)

        self.tree = ttk.Treeview(self.table_frame, columns=("Amount", "Category", "Date"), show="headings")
        self.tree.heading("Amount", text="Amount (₹)")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill=BOTH, expand=True, padx=20)

        self.show_expenses()

    def add_expense(self):
        amt = self.amount_entry.get().strip()
        cat = self.category_entry.get().strip()
        dt = self.date_entry.get_date().strftime("%Y-%m-%d")

        if not (amt and cat):
            messagebox.showerror("Input Error", "All fields are required.")
            return
        try:
            amt = float(amt)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number.")
            return

        self.cur.execute("INSERT INTO expenses (username, amount, category, date) VALUES (?, ?, ?, ?)",
                         (self.user, amt, cat, dt))
        self.conn.commit()

        self.amount_entry.delete(0, END)
        self.category_entry.delete(0, END)
        self.show_expenses()
        self.check_budget()

    def show_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cur.execute("SELECT amount, category, date FROM expenses WHERE username=?", (self.user,))
        for row in self.cur.fetchall():
            self.tree.insert("", END, values=row)

    def apply_filter(self):
        cat = self.filter_category.get().strip()
        start = self.filter_start.get_date().strftime("%Y-%m-%d")
        end = self.filter_end.get_date().strftime("%Y-%m-%d")

        query = "SELECT amount, category, date FROM expenses WHERE username=?"
        params = [self.user]
        if cat:
            query += " AND category LIKE ?"
            params.append(f"%{cat}%")
        if start and end:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start, end])

        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cur.execute(query, tuple(params))
        for row in self.cur.fetchall():
            self.tree.insert("", END, values=row)

    def export_to_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", title="Save CSV File",
                                                filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        self.cur.execute("SELECT amount, category, date FROM expenses WHERE username=?", (self.user,))
        rows = self.cur.fetchall()
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Amount", "Category", "Date"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Expenses exported to {filename}")

    def show_charts(self):
        self.cur.execute("SELECT category, SUM(amount) FROM expenses WHERE username=? GROUP BY category", (self.user,))
        data = self.cur.fetchall()
        if not data:
            messagebox.showinfo("Info", "No data to show.")
            return
        categories, totals = zip(*data)
        plt.figure(figsize=(6, 6))
        plt.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title("Expense by Category")
        plt.show()

    def set_budget_popup(self):
        popup = Toplevel(self.root)
        popup.title("Set Monthly Budget")
        Label(popup, text="Enter monthly budget:").pack(padx=10, pady=5)
        entry = Entry(popup)
        entry.pack(pady=5)
        Button(popup, text="Save", command=lambda: self.save_budget(entry.get(), popup)).pack(pady=5)

    def save_budget(self, value, popup):
        try:
            val = float(value)
            self.cur.execute("REPLACE INTO budgets (username, budget) VALUES (?, ?)", (self.user, val))
            self.conn.commit()
            self.budget = val
            popup.destroy()
            messagebox.showinfo("Budget", "Monthly budget set successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid number.")

    def check_budget(self):
        today = datetime.now().strftime("%Y-%m")
        self.cur.execute("SELECT SUM(amount) FROM expenses WHERE username=? AND strftime('%Y-%m', date)=?",
                         (self.user, today))
        total = self.cur.fetchone()[0] or 0
        if self.budget > 0:
            if total >= self.budget:
                messagebox.showwarning("Budget Alert", "You have exceeded your monthly budget!")
            elif total >= 0.8 * self.budget:
                messagebox.showinfo("Budget Alert", "You have crossed 80% of your monthly budget.")

if __name__ == "__main__":
    root = Tk()
    app = SmartExpenseManager(root)
    root.mainloop()