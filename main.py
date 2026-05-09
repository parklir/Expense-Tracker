import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

def load_expenses():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_expenses():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=4)

def add_expense():
    amount = entry_amount.get().strip()
    category = category_var.get()
    date = entry_date.get().strip()

    if not amount or not date:
        messagebox.showwarning("Ошибка", "Заполните все поля")
        return

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Сумма должна быть числом")
        return

    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ДД-ММ-ГГГГ")
        return

    expenses.append({
        "amount": amount_val,
        "category": category,
        "date": date
    })
    save_expenses()
    update_table()
    clear_inputs()

def clear_inputs():
    entry_amount.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    category_var.set("Еда")

def update_table():
    for row in table.get_children():
        table.delete(row)

    filtered = expenses
    filter_category = filter_category_var.get()
    filter_date = entry_filter_date.get().strip()

    if filter_category != "Все":
        filtered = [e for e in filtered if e["category"] == filter_category]
    if filter_date:
        try:
            datetime.strptime(filter_date, "%d-%m-%Y")
            filtered = [e for e in filtered if e["date"] == filter_date]
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат даты фильтра")

    for expense in filtered:
        table.insert("", tk.END, values=(
            expense["date"],
            expense["category"],
            f"{expense['amount']:.2f}"
        ))

    calculate_total(filtered)

def calculate_total(expenses_list):
    total = sum(e["amount"] for e in expenses_list)
    total_label.config(text=f"Общая сумма: {total:.2f} руб.")

def calculate_period():
    start_date = entry_start_date.get().strip()
    end_date = entry_end_date.get().strip()

    if not start_date or not end_date:
        messagebox.showwarning("Ошибка", "Введите начальную и конечную дату")
        return

    try:
        start = datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.strptime(end_date, "%d-%m-%Y")
    except ValueError:
        messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ДД-ММ-ГГГГ")
        return

    total = 0
    for expense in expenses:
        expense_date = datetime.strptime(expense["date"], "%d-%m-%Y")
        if start <= expense_date <= end:
            total += expense["amount"]

    period_label.config(text=f"Сумма за период {start_date} - {end_date}: {total:.2f} руб.")

def apply_filter():
    update_table()

def reset_filter():
    filter_category_var.set("Все")
    entry_filter_date.delete(0, tk.END)
    update_table()

def delete_selected():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите расход для удаления")
        return

    if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
        item = selected[0]
        values = table.item(item, "values")
        for i, expense in enumerate(expenses):
            if (expense["date"] == values[0] and 
                expense["category"] == values[1] and 
                f"{expense['amount']:.2f}" == values[2]):
                expenses.pop(i)
                break
        save_expenses()
        update_table()

expenses = load_expenses()

window = tk.Tk()
window.title("Expense Tracker")
window.geometry("950x700")

# === Форма добавления ===
input_frame = tk.LabelFrame(window, text="Добавить расход", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=5)

tk.Label(input_frame, text="Сумма (руб):").grid(row=0, column=0, sticky="w")
entry_amount = tk.Entry(input_frame)
entry_amount.grid(row=0, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky="w")
category_var = tk.StringVar(value="Еда")
category_combo = ttk.Combobox(input_frame, textvariable=category_var, 
                               values=["Еда", "Транспорт", "Развлечения", "Коммунальные", "Здоровье", "Другое"], width=15)
category_combo.grid(row=1, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Дата (ДД-ММ-ГГГГ):").grid(row=2, column=0, sticky="w")
entry_date = tk.Entry(input_frame)
entry_date.grid(row=2, column=1, padx=5, pady=2)

tk.Button(input_frame, text="Добавить расход", command=add_expense, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

# === Фильтрация ===
filter_frame = tk.LabelFrame(window, text="Фильтрация", padx=10, pady=10)
filter_frame.pack(fill="x", padx=10, pady=5)

tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
filter_category_var = tk.StringVar(value="Все")
filter_category_combo = ttk.Combobox(filter_frame, textvariable=filter_category_var, 
                                      values=["Все", "Еда", "Транспорт", "Развлечения", "Коммунальные", "Здоровье", "Другое"], width=12)
filter_category_combo.grid(row=0, column=1, padx=5)

tk.Label(filter_frame, text="Дата:").grid(row=0, column=2, sticky="w")
entry_filter_date = tk.Entry(filter_frame, width=12)
entry_filter_date.grid(row=0, column=3, padx=5)

tk.Button(filter_frame, text="Применить", command=apply_filter).grid(row=0, column=4, padx=5)
tk.Button(filter_frame, text="Сбросить", command=reset_filter).grid(row=0, column=5, padx=5)

# === Подсчёт суммы за период ===
period_frame = tk.LabelFrame(window, text="Подсчёт расходов за период", padx=10, pady=10)
period_frame.pack(fill="x", padx=10, pady=5)

tk.Label(period_frame, text="От (ДД-ММ-ГГГГ):").grid(row=0, column=0, sticky="w")
entry_start_date = tk.Entry(period_frame, width=12)
entry_start_date.grid(row=0, column=1, padx=5)

tk.Label(period_frame, text="До (ДД-ММ-ГГГГ):").grid(row=0, column=2, sticky="w")
entry_end_date = tk.Entry(period_frame, width=12)
entry_end_date.grid(row=0, column=3, padx=5)

tk.Button(period_frame, text="Рассчитать", command=calculate_period, bg="blue", fg="white").grid(row=0, column=4, padx=5)

period_label = tk.Label(period_frame, text="", font=("Arial", 10))
period_label.grid(row=1, column=0, columnspan=5, pady=5)

# === Таблица ===
table_frame = tk.LabelFrame(window, text="Список расходов", padx=10, pady=10)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("date", "category", "amount")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
table.heading("date", text="Дата")
table.heading("category", text="Категория")
table.heading("amount", text="Сумма (руб)")
table.column("date", width=100)
table.column("category", width=120)
table.column("amount", width=100)
table.pack(fill="both", expand=True)

# === Кнопка удаления и общая сумма ===
bottom_frame = tk.Frame(window)
bottom_frame.pack(fill="x", padx=10, pady=5)

tk.Button(bottom_frame, text="Удалить выбранный", command=delete_selected, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

total_label = tk.Label(bottom_frame, text="Общая сумма: 0.00 руб.", font=("Arial", 11, "bold"))
total_label.pack(side=tk.RIGHT, padx=5)

update_table()
window.mainloop()