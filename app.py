from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from blockchain import init_db, add_block, get_chain, verify_chain, get_db

app = Flask(__name__)
app.secret_key = "trustfund-secret-key"

init_db()


def create_admin():
    conn = get_db()
    row = conn.execute("SELECT id FROM users WHERE role='admin'").fetchone()
    if not row:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            ("NGO Admin", "admin@trustfund.com", generate_password_hash("admin123"), "admin"))
        conn.commit()
    conn.close()


create_admin()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        exists = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if exists:
            conn.close()
            return render_template("register.html", error="This email address is already registered.")
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            (name, email, generate_password_hash(password), "donor"))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect("/")
        return render_template("login.html", error="Incorrect email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        name = request.form["name"].strip()
        try:
            amount = float(request.form["amount"])
        except ValueError:
            return render_template("donate.html", error="Please enter a valid numeric amount.")
        if not name or amount <= 0:
            return render_template("donate.html", error="Please enter a valid name and an amount greater than zero.")
        receipt = add_block("donation", amount, name)
        return render_template("receipt.html", name=name, amount=amount, receipt=receipt)
    return render_template("donate.html")


@app.route("/expense", methods=["GET", "POST"])
def expense():
    if session.get("role") != "admin":
        return redirect("/login")
    if request.method == "POST":
        purpose = request.form["purpose"].strip()
        try:
            amount = float(request.form["amount"])
        except ValueError:
            return render_template("expense.html", error="Please enter a valid numeric amount.")
        if not purpose or amount <= 0:
            return render_template("expense.html", error="Please enter a valid purpose and an amount greater than zero.")
        h = add_block("expense", amount, purpose)
        return render_template("expense.html", success="Expense recorded successfully. Block hash: " + h)
    return render_template("expense.html")


@app.route("/ledger")
def ledger():
    chain = get_chain()
    return render_template("ledger.html", chain=chain)


@app.route("/dashboard")
def dashboard():
    chain = get_chain()
    received = sum(b["amount"] for b in chain if b["type"] == "donation")
    spent = sum(b["amount"] for b in chain if b["type"] == "expense")
    balance = received - spent
    donors = len([b for b in chain if b["type"] == "donation"])
    valid, bad_idx, msg = verify_chain()
    return render_template("dashboard.html", received=received, spent=spent,
                           balance=balance, donors=donors, valid=valid, bad_idx=bad_idx)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    valid, bad_idx, msg = verify_chain()
    result = {"valid": valid, "bad_idx": bad_idx, "msg": msg}
    found = None
    searched = None
    if request.method == "POST":
        searched = request.form["receipt"].strip()
        for b in get_chain():
            if b["hash"] == searched:
                found = b
                break
    return render_template("verify.html", result=result, found=found, searched=searched)


if __name__ == "__main__":
    app.run(debug=True)