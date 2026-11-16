import os
from datetime import datetime, timedelta

import pymysql
from flask import Flask, render_template_string

app = Flask(__name__)

SERVER_A_COUNTER = "http://195.148.21.16/viikko2/"
SERVER_B_COUNTER = "http://128.214.255.114/viikko4/"
GITHUB_URL = "https://github.com/coffeeMusic83/Linux-Administration/tree/main/viikko4"


def get_connection():
    # Connects to B's LOCAL MariaDB (the replica) with a SELECT-only user.
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def boot_time():
    """When server B was last started (read from /proc/uptime)."""
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.read().split()[0])
        return (datetime.now() - timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return "unknown"


def read_counter_and_status():
    """Only reads. This page never modifies the database."""
    visits, status, error = None, None, None
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SET SESSION TRANSACTION READ ONLY")
                cur.execute("SELECT visits FROM counter WHERE id = 1")
                row = cur.fetchone()
                visits = row["visits"] if row else None
                try:
                    cur.execute("SHOW SLAVE STATUS")
                    status = cur.fetchone()
                except pymysql.MySQLError:
                    status = None
        finally:
            conn.close()
    except pymysql.MySQLError as e:
        error = str(e.args[-1]) if e.args else "database error"
    return visits, status, error


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Week 4 – Read-only replica (server B)</title>
  <style>
    :root { --bg:#0d1117; --card:#161b22; --border:#30363d; --text:#e6edf3;
            --muted:#8b949e; --green:#39ff14; --orange:#e8590c; --purple:#8a3ffc;
            --pink:#e60ad6; --red:#ff5555; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text);
           font-family:system-ui,-apple-system,"Segoe UI",sans-serif; line-height:1.6; }
    .wrap { max-width:820px; margin:0 auto; padding:24px 16px 40px; }
    .mono, code, pre { font-family:"Consolas","Courier New",monospace; }
    .term { background:var(--card); border:1px solid var(--border); border-radius:10px; overflow:hidden; }
    .term-bar { padding:10px 14px; border-bottom:1px solid var(--border); color:var(--muted); font-size:13px; }
    .dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:5px; }
    .term-body { padding:18px 20px; }
    .prompt { color:var(--green); font-weight:bold; }
    h1 { font-family:"Consolas","Courier New",monospace; color:var(--green); font-size:2.1rem; margin:10px 0 4px; }
    h2 { font-family:"Consolas","Courier New",monospace; color:var(--orange); font-size:1.15rem;
         border-bottom:1px dashed var(--border); padding-bottom:8px; margin:36px 0 14px; }
    h2 span { color:var(--muted); margin-right:6px; }
    h3 { color:var(--purple); font-size:1rem; margin:18px 0 6px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:18px 20px; }
    .badge { display:inline-block; border:2px solid var(--pink); color:var(--pink); border-radius:999px;
             padding:3px 14px; font-family:"Consolas","Courier New",monospace; font-weight:bold;
             letter-spacing:1px; box-shadow:0 0 10px rgba(230,10,214,.35); }
    .counter { font-family:"Consolas","Courier New",monospace; font-size:3.5rem; color:var(--green);
               text-align:center; margin:4px 0; text-shadow:0 0 12px rgba(57,255,20,.35); }
    .center { text-align:center; color:var(--muted); }
    code { color:var(--green); }
    pre { background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:12px;
          overflow-x:auto; color:#f0e68c; font-size:14px; }
    .flow { display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:center; }
    .box { border:1px solid var(--purple); border-radius:8px; padding:6px 12px;
           font-family:"Consolas","Courier New",monospace; font-size:14px; }
    .box.a { border-color:var(--orange); }
    .box.b { border-color:var(--pink); }
    .arrow { color:var(--muted); }
    table { border-collapse:collapse; width:100%; font-size:15px; }
    th, td { border:1px solid var(--border); padding:8px 10px; text-align:left; vertical-align:top; }
    th { background:#21262d; color:var(--purple); }
    .ok { color:var(--green); font-weight:bold; }
    .bad { color:var(--red); font-weight:bold; }
    .pending { color:var(--orange); }
    ul { margin:0; padding-left:20px; }
    a { color:var(--purple); }
    .links a { display:inline-block; margin:4px 8px; }
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
      ubuntu@server-b: ~/viikko4
    </div>
    <div class="term-body mono">
      <div><span class="prompt">ubuntu@server-b:~$</span> python3 app.py --read-only</div>
      <h1>Week 4: Backups &amp; Replication</h1>
      <div style="color:var(--muted)">Server B – a clone of server A with hourly file backups and a live MariaDB replica.</div>
      <div style="margin-top:12px"><span class="badge">READ-ONLY REPLICA</span></div>
    </div>
  </div>

  <h2><span>00</span>Replicated visitor counter</h2>
  <div class="card">
    {% if error %}
      <div class="center bad">Database error: {{ error }}</div>
    {% else %}
      <div class="center">Server A's Week 2 page has been loaded</div>
      <div class="counter">{{ visits }}</div>
      <div class="center">times (read from <strong>server B's local replicated database</strong>)</div>
    {% endif %}
    <p class="center" style="margin-bottom:0">Loading this page does <strong>not</strong> change the counter.
       Open server A's page to increase it, then reload this page.</p>
    <div class="center links">
      <a href="{{ a_url }}">Server A: /viikko2/ (increments)</a>
      <a href="{{ b_url }}">Server B: /viikko4/ (read-only)</a>
    </div>
  </div>

  <h2><span>01</span>Live replication status</h2>
  <div class="card">
    {% if status %}
    <table>
      <tr><th>Field</th><th>Value</th></tr>
      <tr><td>Master host (server A, private network)</td><td class="mono">{{ status.Master_Host }}</td></tr>
      <tr><td>Slave_IO_Running</td>
          <td class="{{ 'ok' if status.Slave_IO_Running == 'Yes' else 'bad' }}">{{ status.Slave_IO_Running }}</td></tr>
      <tr><td>Slave_SQL_Running</td>
          <td class="{{ 'ok' if status.Slave_SQL_Running == 'Yes' else 'bad' }}">{{ status.Slave_SQL_Running }}</td></tr>
      <tr><td>Seconds_Behind_Master</td><td class="mono">{{ status.Seconds_Behind_Master }}</td></tr>
      <tr><td>Last error</td><td class="mono">{{ status.Last_Error or '-' }}</td></tr>
    </table>
    {% else %}
      <p class="pending" style="margin:0">Replication status not available to this user.</p>
    {% endif %}
    <p class="center" style="margin-bottom:0">Checked {{ checked_at }} · Server B last booted {{ booted }}</p>
  </div>

  <h2><span>02</span>Architecture</h2>
  <div class="card">
    <div class="flow">
      <span class="box a">A: Browser → Nginx → Flask /viikko2/</span><span class="arrow">→</span>
      <span class="box a">MariaDB (master, binlog)</span><span class="arrow">⇒ replication ⇒</span>
      <span class="box b">B: MariaDB (replica, read_only)</span><span class="arrow">→</span>
      <span class="box b">Flask /viikko4/ → Nginx → Browser</span>
    </div>
    <div class="flow" style="margin-top:12px">
      <span class="box a">A: /var/www/html</span><span class="arrow">⇒ cron every hour (tar + SSH) ⇒</span>
      <span class="box b">B: /srv/backups/server-a/</span>
    </div>
    <p style="margin-bottom:0">Replication and backups use the cPouta private network (A = 192.168.1.204, B = 192.168.1.64).
       The database port is not open to the internet.</p>
  </div>

  <h2><span>03</span>How server B was created</h2>
  <div class="card">
    <ul>
      <li>Took a snapshot of server A in cPouta (<code>server-a-week4</code>).</li>
      <li>Launched a new instance <code>server-b</code> from the snapshot: same flavor (standard.large), same network,
          same security group and key pair.</li>
      <li>Allocated a new floating IP for B (<code>128.214.255.114</code>). A keeps <code>195.148.21.16</code>.</li>
      <li>On B: changed the hostname to <code>server-b</code> and disabled the copied Week 2 service
          (<code>viikko2.service</code>) so B never writes to its own database.</li>
      <li>A's Week 2 application and Week 3 report keep running at their original URLs.</li>
    </ul>
  </div>

  <h2><span>04</span>Storage layout and backup locations</h2>
  <div class="card">
    <table>
      <tr><th>Path</th><th>Server A</th><th>Server B</th></tr>
      <tr><td class="mono">/var/www/html</td><td>Web root (Week 1 page, Week 3 report) – <strong>backed up</strong></td><td>Copy from the snapshot</td></tr>
      <tr><td class="mono">/var/lib/mysql</td><td>MariaDB data (master)</td><td>MariaDB data (replica)</td></tr>
      <tr><td class="mono">/var/log/mysql</td><td>Binary logs (kept 7 days)</td><td>Relay logs</td></tr>
      <tr><td class="mono">/home/ubuntu/viikko2</td><td>Week 2 app + <code>.env</code></td><td>Copy, service disabled</td></tr>
      <tr><td class="mono">/home/ubuntu/viikko4</td><td>–</td><td>This read-only app + <code>.env</code></td></tr>
      <tr><td class="mono">/home/ubuntu/backup-logs</td><td>Backup log (SUCCESS / FAILED per run)</td><td>–</td></tr>
      <tr><td class="mono">/srv/backups/server-a</td><td>–</td><td><strong>Backup archives</strong> (outside the web root)</td></tr>
    </table>
  </div>

  <h2><span>05</span>Users, ownership and permissions</h2>
  <div class="card">
    <h3>Linux users</h3>
    <table>
      <tr><th>User</th><th>Server</th><th>Purpose</th></tr>
      <tr><td class="mono">ubuntu</td><td>A, B</td><td>Admin user (sudo). Runs the Flask apps and the backup cron job on A.</td></tr>
      <tr><td class="mono">webbackup</td><td>B</td><td>Receives backups. No password, SSH key only. The key only works from
          A's private IP and cannot open a shell or tunnels (<code>from=</code>, <code>no-pty</code>, <code>no-port-forwarding</code>).</td></tr>
    </table>
    <h3>Files</h3>
    <ul>
      <li><code>/srv/backups/server-a</code> – owner <code>webbackup</code>, mode <code>700</code>; archives mode <code>600</code>.</li>
      <li>Even the admin user <code>ubuntu</code> cannot list the backup directory without <code>sudo</code>
          (noticed during the restore test: <code>ls html-*.tar.gz</code> failed until run with <code>sudo sh -c</code>).</li>
      <li><code>~/.ssh/backup_to_b</code> on A – private key, mode <code>600</code>.</li>
      <li><code>.env</code> files with database passwords are not in Git and not under the web root.</li>
    </ul>
    <h3>Database users</h3>
    <table>
      <tr><th>User</th><th>Server</th><th>Privileges</th></tr>
      <tr><td class="mono">viikko2user</td><td>A</td><td>Week 2 app, reads and updates the counter.</td></tr>
      <tr><td class="mono">repl@192.168.1.64</td><td>A</td><td><code>REPLICATION SLAVE</code> only, and only from B's private IP.</td></tr>
      <tr><td class="mono">viikko4reader@localhost</td><td>B</td><td><code>SELECT</code> on <code>viikko2.counter</code> + replication monitoring. Cannot write.</td></tr>
    </table>
    <p style="margin-bottom:0">B's MariaDB also runs with <code>read_only = 1</code>, so ordinary users cannot modify data even by mistake.
       Only the replication thread applies changes from A.</p>
  </div>

  <h2><span>06</span>Hourly backups</h2>
  <div class="card">
    <ul>
      <li>Cron on A runs <code>backup.sh</code> every hour at minute 7: <code>7 * * * *</code>.</li>
      <li>The script packs <code>/var/www/html</code> with <code>tar</code> and streams it over SSH to B as
          <code>html-YYYYMMDD-HHMMSS.tar.gz</code>.</li>
      <li>The file is written as <code>.part</code> first and renamed only after a successful transfer.</li>
      <li>Every run is logged as <code>SUCCESS</code> or <code>FAILED</code> in <code>/home/ubuntu/backup-logs/backup.log</code>.</li>
      <li>The newest 48 versions (2 days) are kept; older ones are removed automatically.</li>
    </ul>
  </div>

  <h2><span>07</span>Continuous replication</h2>
  <div class="card">
    <ul>
      <li>A writes every change of the <code>viikko2</code> database to its binary log (<code>server-id = 1</code>).</li>
      <li>B (<code>server-id = 2</code>) connects to A as <code>repl</code>, copies the changes to its relay log and applies them.</li>
      <li>The cPouta security group allows port 3306 only from <code>192.168.1.64/32</code>.</li>
      <li>Replication starts automatically when MariaDB starts, also after a reboot.</li>
    </ul>
    <h3>Why replication does not replace backups</h3>
    <p style="margin-bottom:0">Replication copies every change immediately – including mistakes. If a table is deleted or data is
       corrupted on A, the same happens on B within seconds. Historical backups keep older versions, so data can be
       restored to the state before the mistake.</p>
  </div>

  <h2><span>08</span>Test results</h2>
  <div class="card">
    <table>
      <tr><th>Test</th><th>Result</th></tr>
      <tr><td>Both pages are publicly accessible</td>
          <td class="ok">OK (16 Nov 2026) – A's /viikko2/ and B's /viikko4/ open from a normal browser.</td></tr>
      <tr><td>Loading A's page updates the counter shown on B</td>
          <td class="ok">OK (16 Nov 2026) – B showed 79, A was loaded once (80), after reload B showed 80.</td></tr>
      <tr><td>Loading B's page does not increment the counter</td>
          <td class="ok">OK (16 Nov 2026) – reloading B several times kept the value unchanged.</td></tr>
      <tr><td>Replication reports normal operation <span style="color:var(--muted)">(live)</span></td>
          {% if repl_ok %}<td class="ok">OK now – Slave_IO_Running: Yes, Slave_SQL_Running: Yes, {{ status.Seconds_Behind_Master }} s behind.</td>
          {% else %}<td class="bad">NOT OK now – see section 01.</td>{% endif %}</tr>
      <tr><td>Two scheduled backups succeeded</td>
          <td class="ok">OK – cron runs logged on A as <code>SUCCESS</code> at 2026-11-16 23:07:02
          (<code>html-20261116-230701.tar.gz</code>) and 2026-11-17 00:07:02 (<code>html-20261117-000701.tar.gz</code>).
          Both archives are on B in <code>/srv/backups/server-a</code> with mode 600. The 23:07 run was the first one after B's reboot.</td></tr>
      <tr><td>Restored test file matches the original</td>
          <td class="ok">OK (16 Nov 2026) – <code>html/index.html</code> restored from
          <code>html-20261116-220655.tar.gz</code> to <code>/srv/restore-test</code> on B.
          SHA-256 identical on A and B: <code>c322cd19…e629c4</code>.</td></tr>
      <tr><td>Website, replication and backups work after rebooting B</td>
          <td class="ok">OK (16 Nov 2026) – after <code>sudo reboot</code>: nginx, mariadb and viikko4 active,
          replication Yes / Yes / 0, counter on B kept updating. Backup runs after the reboot: see backup row.</td></tr>
    </table>
  </div>

  <h2><span>09</span>Problem I solved</h2>
  <div class="card">
    <p style="margin:0">With two terminal windows open, I created server A's replication config on server B by mistake.
       Because B is a clone of A, both servers have the same files and settings, so the commands worked without errors.
       I noticed the mistake from the prompt: I had changed B's hostname to <code>server-b</code> right after creating it,
       so the prompt showed which server I was on. I fixed it by replacing the file with the replica settings
       (<code>server-id = 2</code>, <code>read_only = 1</code>) and resetting B's binary log, and then created the master
       config on A. Lesson learned: always check the prompt before running a command when working with several servers.</p>
  </div>

  <h2><span>10</span>Source code</h2>
  <div class="card">
    <p style="margin:0">GitHub: <a href="{{ github }}">github.com/coffeeMusic83/Linux-Administration</a> (folder <code>viikko4/</code>)<br>
    <span style="color:var(--muted)">No passwords, keys, SQL dumps or backup archives are published.</span></p>
  </div>

  <footer>Served by Nginx + Gunicorn on server B · Ubuntu 22.04 LTS · CSC cPouta · Week 4</footer>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    visits, status, error = read_counter_and_status()
    repl_ok = bool(status) and status.get("Slave_IO_Running") == "Yes" \
        and status.get("Slave_SQL_Running") == "Yes"
    return render_template_string(
        PAGE,
        repl_ok=repl_ok,
        booted=boot_time(),
        visits=visits,
        status=status,
        error=error,
        checked_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        a_url=SERVER_A_COUNTER,
        b_url=SERVER_B_COUNTER,
        github=GITHUB_URL,
    )
