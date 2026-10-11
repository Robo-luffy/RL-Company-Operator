from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from db import init_db, list_employees, list_expenses, get_expense, submit_approval, get_approval
app = FastAPI(title="starX Company Platform")
init_db()

def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title} | starX Workspace</title>
<style>
body{{font-family:Arial,sans-serif;max-width:960px;margin:32px auto;padding:0 20px;color:#172033;background:#f6f8fb}}
header{{background:#14213d;color:white;padding:20px 24px;border-radius:12px}}
nav{{margin:18px 0;display:flex;gap:16px}}nav a{{color:#175cd3;text-decoration:none;font-weight:bold}}
.card{{background:white;border:1px solid #dce2ea;border-radius:10px;padding:18px;margin:16px 0}}
button{{background:#175cd3;color:white;border:0;padding:10px 14px;border-radius:6px;cursor:pointer}}
input{{padding:10px;border:1px solid #cbd5e1;border-radius:6px}}
table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:12px;border-bottom:1px solid #e5e7eb;text-align:left}}
</style></head><body><header><h1>Acme Workspace</h1><div>Internal employee operations portal · Demo environment</div></header>
<nav><a href="/">Home</a><a href="/employees">Employees</a><a href="/expenses">Expenses</a><a href="/approvals">Approvals</a></nav>{body}</body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return page("Home", "<section class='card'><h2>Welcome to starX Workspace</h2><p>Internal operations demo.</p><a href='/expenses'>Open Expenses</a></section>")

@app.get("/employees", response_class=HTMLResponse)
def employees():
    rows = "".join(f"<tr><td>{e['employee_id']}</td><td>{e['name']}</td><td>{e['department']}</td></tr>" for e in list_employees())
    return page("Employees", f"<section class='card'><h2>Employees</h2><table><tr><th>ID</th><th>Name</th><th>Department</th></tr>{rows}</table></section>")

@app.get("/expenses", response_class=HTMLResponse)
def expenses(employee: str = ""):
    rows = "".join(f"<tr><td>{e['expense_id']}</td><td>{e['employee_name']}</td><td>{e['category']}</td><td>₹{e['amount']:.2f}</td><td>{e['status']}</td><td><a href='/expenses/{e['expense_id']}'>Open {e['expense_id']}</a></td></tr>" for e in list_expenses(employee))
    body = f"""<section class='card'><h2>Expenses</h2><form action='/expenses' method='get'>
<label for='employee'>Employee name</label> <input id='employee' name='employee' value='{employee}' placeholder='Search employee'/>
<button type='submit'>Search</button></form></section>
<section class='card'><table><tr><th>Expense ID</th><th>Employee</th><th>Category</th><th>Amount</th><th>Status</th><th>Action</th></tr>{rows}</table></section>"""
    return page("Expenses", body)

@app.get("/expenses/{expense_id}", response_class=HTMLResponse)
def expense_detail(expense_id: str):
    e = get_expense(expense_id)

    if not e:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    if e["status"] == "pending_approval":
        action = ""
        confirmation = "Approval request submitted"
    else:
        action = f"""
        <form method="post" action="/approvals/{expense_id}">
            <button type="submit">Submit for Approval</button>
        </form>
        """
        confirmation = ""

    body = f"""
    <section class='card'>
        <h2>Expense {e['expense_id']}</h2>
        <p><b>Employee:</b> {e['employee_name']}</p>
        <p><b>Category:</b> {e['category']}</p>
        <p><b>Amount:</b> ₹{e['amount']:.2f}</p>
        <p><b>Description:</b> {e['description']}</p>
        <p>
            <b>Status:</b>
            <span id='expense-status'>{e['status']}</span>
        </p>
        {action}
        <p id='confirmation'>{confirmation}</p>
    </section>
    """

    return page(f"Expense {expense_id}", body)


@app.post("/approvals/{expense_id}")
def submit_approval_ui(expense_id: str):
    try: submit_approval(expense_id)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse(url=f"/expenses/{expense_id}", status_code=303)

@app.get("/approvals", response_class=HTMLResponse)
def approvals():
    rows = []
    for e in list_expenses():
        approval = get_approval(e["expense_id"])
        if approval: rows.append(f"<tr><td>{e['expense_id']}</td><td>{e['employee_name']}</td><td>{approval['status']}</td></tr>")
    return page("Approvals", f"<section class='card'><h2>Approval requests</h2><table><tr><th>Expense</th><th>Employee</th><th>Status</th></tr>{''.join(rows) or '<tr><td colspan=3>No approval requests yet.</td></tr>'}</table></section>")

@app.get("/api/health")
def health(): return {"status": "ok"}
