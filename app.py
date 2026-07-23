from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        venue TEXT,
        description TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS registrations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        name TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    conn.commit()

    c.execute("SELECT COUNT(*) FROM events")
    if c.fetchone()[0] == 0:
        sample_events = [
            ("Python Workshop", "10 Aug 2026", "Online",
             "Learn Python from scratch."),
            ("AI Bootcamp", "15 Aug 2026", "Bangalore",
             "Hands-on Artificial Intelligence workshop."),
            ("Web Development Seminar", "20 Aug 2026", "Mangalore",
             "Learn HTML, CSS, JavaScript and Flask.")
        ]

        c.executemany(
            "INSERT INTO events(title,date,venue,description) VALUES(?,?,?,?)",
            sample_events
        )

    conn.commit()
    conn.close()


init_db()

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("SELECT * FROM events")
    events = c.fetchall()

    conn.close()

    return render_template("index.html", events=events)

# ---------------- EVENT DETAILS ---------------- #

@app.route("/event/<int:event_id>")
def event(event_id):
    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = c.fetchone()

    conn.close()

    return render_template("event.html", event=event)

# ---------------- REGISTER ---------------- #

@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        conn = sqlite3.connect("events.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO registrations(event_id,name,email,phone) VALUES(?,?,?,?)",
            (event_id, name, email, phone)
        )

        conn.commit()
        conn.close()

        return redirect("/success")

    return render_template("register.html", event_id=event_id)

# ---------------- SUCCESS ---------------- #

@app.route("/success")
def success():
    return render_template("success.html")

# ---------------- REGISTRATIONS ---------------- #

@app.route("/registrations")
def registrations():

    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("""
    SELECT registrations.id,
           events.title,
           registrations.name,
           registrations.email,
           registrations.phone
    FROM registrations
    JOIN events
    ON registrations.event_id = events.id
    """)

    data = c.fetchall()

    conn.close()

    return render_template("registrations.html", registrations=data)

# ---------------- DELETE ---------------- #

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("events.db")
    c = conn.cursor()

    c.execute("DELETE FROM registrations WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/registrations")


if __name__ == "__main__":
    app.run(debug=True)