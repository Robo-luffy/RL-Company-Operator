import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent / "company.db"
def connect():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row; return con
def init_db():
    with connect() as con:
        con.execute("CREATE TABLE IF NOT EXISTS employees (employee_id TEXT PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL)")
        con.execute("""CREATE TABLE IF NOT EXISTS expenses (expense_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, employee_name TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS approvals (approval_id INTEGER PRIMARY KEY AUTOINCREMENT, expense_id TEXT NOT NULL UNIQUE, status TEXT NOT NULL, submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        if con.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            con.executemany("INSERT INTO employees VALUES (?, ?, ?)", [
                ("EMP001","Rahul Sharma","Engineering"),("EMP002","Priya Das","Finance"),("EMP003","Arjun Sen","Operations")])
            con.executemany("""INSERT INTO expenses (expense_id,employee_id,employee_name,category,amount,description,status,created_at) VALUES (?,?,?,?,?,?,?,?)""", [
                ("EXP1022","EMP001","Rahul Sharma","Travel",3200.0,"Train travel for customer visit","draft","2026-10-02"),
                ("EXP1023","EMP001","Rahul Sharma","Hotel",9200.0,"Hotel stay during customer visit","draft","2026-10-08"),
                ("EXP2041","EMP002","Priya Das","Meals",1450.0,"Team dinner","draft","2026-10-07")])
def list_employees():
    with connect() as con: return [dict(r) for r in con.execute("SELECT * FROM employees ORDER BY name")]
def search_employee(name):
    with connect() as con:
        row=con.execute("SELECT * FROM employees WHERE name LIKE ? ORDER BY name LIMIT 1",(f"%{name}%",)).fetchone()
        return dict(row) if row else None
def list_expenses(employee_name=""):
    with connect() as con:
        q="SELECT * FROM expenses WHERE employee_name LIKE ? ORDER BY created_at DESC" if employee_name else "SELECT * FROM expenses ORDER BY created_at DESC"
        params=(f"%{employee_name}%",) if employee_name else ()
        return [dict(r) for r in con.execute(q,params)]
def get_latest_expense(employee_id):
    with connect() as con:
        row=con.execute("SELECT * FROM expenses WHERE employee_id=? ORDER BY created_at DESC LIMIT 1",(employee_id,)).fetchone()
        return dict(row) if row else None
def get_expense(expense_id):
    with connect() as con:
        row=con.execute("SELECT * FROM expenses WHERE expense_id=?",(expense_id,)).fetchone()
        return dict(row) if row else None
def submit_approval(expense_id):
    with connect() as con:
        row=con.execute("SELECT * FROM expenses WHERE expense_id=?",(expense_id,)).fetchone()
        if not row: raise ValueError("Expense not found")
        con.execute("UPDATE expenses SET status='pending_approval' WHERE expense_id=?",(expense_id,))
        con.execute("INSERT OR IGNORE INTO approvals (expense_id,status) VALUES (?,'pending_approval')",(expense_id,))
        return {"expense_id":expense_id,"status":"pending_approval"}
def get_approval(expense_id):
    with connect() as con:
        row=con.execute("SELECT * FROM approvals WHERE expense_id=?",(expense_id,)).fetchone()
        return dict(row) if row else None
def get_demo_snapshot():
    with connect() as con:
        return {"employees":con.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
                "expenses":con.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]}


def reset_demo_expense(expense_id="EXP1023"):
    with connect() as con:
        row = con.execute(
            "SELECT expense_id FROM expenses WHERE expense_id = ?",
            (expense_id,),
        ).fetchone()

        if not row:
            raise ValueError(f"Expense {expense_id} not found")

        # Reset the expense to its initial state.
        con.execute(
            "UPDATE expenses SET status = 'draft' WHERE expense_id = ?",
            (expense_id,),
        )

        # Remove the old approval request so it can be submitted again.
        con.execute(
            "DELETE FROM approvals WHERE expense_id = ?",
            (expense_id,),
        )

    return {
        "expense_id": expense_id,
        "status": "draft",
        "message": "Demo expense reset successfully.",
    }

