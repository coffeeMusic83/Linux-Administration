import os
import pymysql
from flask import Flask, render_template_string

app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        autocommit=False,
    )


def increment_and_get_visits():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE counter SET visits = visits + 1 WHERE id = 1")
            cur.execute("SELECT visits FROM counter WHERE id = 1")
            visits = cur.fetchone()[0]
        conn.commit()
        return visits
    finally:
        conn.close()


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Week 2 – Python & MariaDB</title>
  <style>
    :root { --bg:#0d1117; --card:#161b22; --border:#30363d; --text:#e6edf3;
            --muted:#8b949e; --green:#39ff14; --orange:#e8590c; --purple:#8a3ffc; --pink:#e60ad6; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text);
           font-family:system-ui,-apple-system,"Segoe UI",sans-serif; line-height:1.6; }
    .wrap { max-width:720px; margin:0 auto; padding:24px 16px 40px; }
    .mono { font-family:"Consolas","Courier New",monospace; }
    .term { background:var(--card); border:1px solid var(--border); border-radius:10px; overflow:hidden; }
    .term-bar { padding:10px 14px; border-bottom:1px solid var(--border); color:var(--muted); font-size:13px; }
    .dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:5px; }
    .term-body { padding:18px 20px; }
    .prompt { color:var(--green); font-weight:bold; }
    h1 { font-family:"Consolas","Courier New",monospace; color:var(--green); font-size:2.2rem; margin:10px 0 4px; }
    h2 { font-family:"Consolas","Courier New",monospace; color:var(--orange); font-size:1.15rem;
         border-bottom:1px dashed var(--border); padding-bottom:8px; margin:36px 0 14px; }
    h2 span { color:var(--muted); margin-right:6px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:18px 20px; }
    .counter { font-family:"Consolas","Courier New",monospace; font-size:3.5rem; color:var(--green);
               text-align:center; margin:4px 0; text-shadow:0 0 12px rgba(57,255,20,.35); }
    .center { text-align:center; color:var(--muted); }
    code { color:var(--green); font-family:"Consolas","Courier New",monospace; }
    .flow { display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:center; }
    .box { border:1px solid var(--purple); color:var(--text); border-radius:8px; padding:6px 12px;
           font-family:"Consolas","Courier New",monospace; font-size:14px; }
    .arrow { color:var(--muted); }
    ul { margin:0; padding-left:20px; }
    a { color:var(--purple); }
    footer { margin-top:40px; border-top:1px dashed var(--border); padding-top:14px;
             text-align:center; color:var(--muted); font-size:13px; font-family:"Consolas","Courier New",monospace; }
  </style>
</head>
<body>
<div class="wrap">

  <div class="term">
    <div class="term-bar mono">
      <span class="dot" style="background:var(--pink)"></span>
      <span class="dot" style="background:var(--orange)"></span>
      <span class="dot" style="background:var(--purple)"></span>
      ubuntu@cpouta: ~/viikko2
    </div>
    <div class="term-body mono">
      <div><span class="prompt">ubuntu@cpouta:~$</span> python3 app.py --with-database</div>
      <h1>Week 2: Python + MariaDB</h1>
      <div style="color:var(--muted)">A Python web app running next to Nginx, with a visitor counter stored in a database.</div>
    </div>
  </div>

  <h2><span>00</span>Visitor counter</h2>
  <div class="card">
    <div class="center">This page has been loaded</div>
    <div class="counter">{{ visits }}</div>
    <div class="center">times</div>
  </div>

  <h2><span>01</span>How it works</h2>
  <div class="card">
    <div class="flow">
      <span class="box">Browser</span><span class="arrow">→</span>
      <span class="box">Nginx :80</span><span class="arrow">→</span>
      <span class="box">Gunicorn 127.0.0.1:8000</span><span class="arrow">→</span>
      <span class="box">Flask</span><span class="arrow">→</span>
      <span class="box">MariaDB</span>
    </div>
    <p style="margin-bottom:0">Nginx forwards requests under <code>/viikko2/</code> to the Python app,
       which listens only on localhost. The Week 1 page still works at
       <a href="/">the root address</a>.</p>
  </div>

  <h2><span>02</span>How the counter is stored</h2>
  <div class="card">
    <ul>
      <li><strong>Database:</strong> MariaDB, started automatically by systemd.</li>
      <li><strong>Table:</strong> <code>counter</code> with a single row (<code>id</code>, <code>visits</code>).</li>
      <li><strong>On every page load:</strong> <code>UPDATE counter SET visits = visits + 1</code>,
          then the new value is read and shown.</li>
      <li><strong>Autostart:</strong> Nginx, MariaDB and the app (<code>viikko2.service</code>) are all enabled in systemd.</li>
    </ul>
  </div>

  <h2><span>03</span>Reboot test</h2>
  <div class="card">
    <p style="margin:0">Rebooted the virtual machine on 2 Nov 2026. Before the reboot the counter showed 5, and after the reboot the page opened automatically and the counter continued from 6. Nginx, MariaDB and the Python app all started on their own, and the value was kept in the database.</p>
  </div>

  <h2><span>04</span>Source code</h2>
  <div class="card">
    <p style="margin:0">GitHub: <a href="https://github.com/coffeeMusic83/Linux-Administration">github.com/coffeeMusic83/Linux-Administration</a><br>
    <span style="color:var(--muted)">Passwords are kept in a <code>.env</code> file that is not in the repository.</span></p>
  </div>

  <footer>Served by Nginx + Gunicorn on Ubuntu 22.04 LTS · CSC cPouta · Week 2</footer>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, visits=increment_and_get_visits())
