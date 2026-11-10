#!/usr/bin/env bash
# Week 3 – Server Status Report
# Collects server information and generates an HTML report for Nginx.
# Usage:
#   ./report.sh            -> generate the report
#   ./report.sh --test     -> test the disk status logic with 50, 80 and 90
 
set -euo pipefail
 
OUTPUT_DIR="/var/www/html/viikko3"
OUTPUT_FILE="$OUTPUT_DIR/index.html"
GITHUB_URL="https://github.com/coffeeMusic83/Linux-Administration"
WARNING_LIMIT=80
 
# Function: returns OK or WARNING based on the usage percentage
get_disk_status() {
    local usage="$1"
    if [ "$usage" -ge "$WARNING_LIMIT" ]; then
        echo "WARNING"
    else
        echo "OK"
    fi
}
 
# Test mode: check both branches of the if statement
if [ "${1:-}" = "--test" ]; then
    for value in 50 80 90; do
        echo "$value% -> $(get_disk_status "$value")"
    done
    exit 0
fi
 
# Collect information with command substitution and pipes
GENERATED_AT=$(date '+%Y-%m-%d %H:%M:%S %Z (UTC%:z)')
UPTIME_TEXT=$(uptime -p)
BOOT_TIME=$(uptime -s)
DISK_USAGE=$(df -P / | awk 'NR == 2 {print $5}' | tr -d '%')
DISK_STATUS=$(get_disk_status "$DISK_USAGE")
MEM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
MEM_AVAILABLE=$(free -m | awk '/^Mem:/ {print $7}')
 
# Colour for the status cell
if [ "$DISK_STATUS" = "OK" ]; then
    STATUS_COLOR="#39ff14"
else
    STATUS_COLOR="#ff5555"
fi
 
# Write to a temporary file first, then move it into place
TEMP_FILE=$(mktemp "$OUTPUT_DIR/.index.XXXXXX")
 
cat > "$TEMP_FILE" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Week 3 – Server Status Report</title>
  <style>
    body { font-family: Consolas, "DejaVu Sans Mono", monospace; font-size: 17px; max-width: 900px; margin: 40px auto;
           padding: 0 20px; line-height: 1.6; background: #0d1117; color: #c9d1d9; }
    h1 { color: #39ff14; }
    h1::before { content: "guest@server:~$ "; color: #58a6ff; }
    h2, h3 { color: #39ff14; }
    h2::before { content: "> "; }
    section { margin: 24px 0; padding: 24px; background: #161b22;
              border: 1px solid #30363d; border-radius: 8px; }
    .table-container { overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #30363d; padding: 12px; text-align: left; }
    th { background: #21262d; color: #58a6ff; }
    code, pre { background: #0d1117; color: #f0e68c; padding: 2px 5px;
                border-radius: 4px; overflow-wrap: anywhere; }
    pre { padding: 12px; overflow-x: auto; }
    a { color: #58a6ff; }
    .note { color: #8b949e; }
  </style>
</head>
<body>
  <header>
    <h1>Server Status Report</h1>
    <p>Week 3: Linux command line and Bash scripting</p>
    <p>Hi! This page is generated every minute by a Bash script running on my
       CSC cPouta virtual machine (Ubuntu). The same server still runs my Week 1
       page and my Week 2 application.</p>
  </header>
 
  <section>
    <h2>Current server status</h2>
    <div class="table-container">
      <table>
        <thead>
          <tr><th scope="col">Information</th><th scope="col">Value</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Report generated</th><td>$GENERATED_AT</td></tr>
          <tr><th scope="row">Server uptime</th><td>$UPTIME_TEXT (booted $BOOT_TIME)</td></tr>
          <tr><th scope="row">Root filesystem (/) disk usage</th><td>$DISK_USAGE %</td></tr>
          <tr><th scope="row">Disk space status</th>
              <td style="color: $STATUS_COLOR; font-weight: bold;">$DISK_STATUS</td></tr>
          <tr><th scope="row">Total RAM</th><td>$MEM_TOTAL MiB</td></tr>
          <tr><th scope="row">Available RAM</th><td>$MEM_AVAILABLE MiB</td></tr>
        </tbody>
      </table>
    </div>
    <p>Disk space status is <strong>OK</strong> below $WARNING_LIMIT% usage
       and <strong>WARNING</strong> at $WARNING_LIMIT% or above.</p>
    <p class="note">Bash generates this report once per minute.
       Wait approximately 1–2 minutes and reload the page to see a new generation time.</p>
  </section>
 
  <section>
    <h2>Commands used</h2>
    <ul>
      <li><code>date '+%Y-%m-%d %H:%M:%S %Z'</code>: displays the current date,
          time and time zone in the given format.</li>
      <li><code>uptime -p</code>: displays how long the server has been running
          in a readable form. <code>uptime -s</code> shows when it was booted.</li>
      <li><code>df -P / | awk 'NR == 2 {print &#36;5}' | tr -d '%'</code>:
          <code>df</code> prints disk usage of the root filesystem, the pipe passes it
          to <code>awk</code>, which takes the 5th column of the 2nd row (e.g. 23%),
          and <code>tr</code> removes the % sign so the number can be compared.</li>
      <li><code>free -m | awk '/^Mem:/ {print &#36;2}'</code>: <code>free -m</code>
          shows memory in MiB; awk picks the "Mem:" row and prints the total
          (column 2). Column 7 is the available memory.</li>
    </ul>
  </section>
 
  <section>
    <h2>How the script works</h2>
    <p>The script <code>report.sh</code> collects server information using Linux
       commands and stores the results in Bash variables through command
       substitution, for example <code>UPTIME_TEXT=&#36;(uptime -p)</code>.</p>
    <p>The function <code>get_disk_status</code> takes the usage percentage as an
       argument. An <code>if</code> statement compares it with the limit 80
       (<code>-ge</code> = greater than or equal): 80 or more returns
       <strong>WARNING</strong>, otherwise <strong>OK</strong>.</p>
    <p>The script writes the HTML into a temporary file and then moves the
       completed file into place as <code>index.html</code>, so a visitor never
       sees a half-written page. Nginx serves this file at <code>/viikko3/</code>.</p>
  </section>
 
  <section>
    <h2>Scheduling</h2>
    <p>I used <strong>cron</strong>. My user's crontab contains this line:</p>
    <pre>* * * * * /home/ubuntu/Linux-Administration/viikko3/report.sh</pre>
    <p>The five asterisks mean "every minute". The cron service is enabled in
       systemd, so it starts automatically after a reboot and the schedule
       continues without any manual action.</p>
  </section>
 
  <section>
    <h2>Test results</h2>
 
    <h3>Syntax check and manual execution</h3>
    <p><code>bash -n report.sh</code> printed nothing, which means there were no
       syntax errors. <code>wc -l</code> confirmed that the whole file was copied to
       the server. Running <code>./report.sh</code> manually created
       <code>index.html</code> and the page opened correctly in the browser.</p>
 
    <h3>Disk space status tests</h3>
    <p>I ran <code>./report.sh --test</code>, which passes the values 50, 80 and 90
       to the same function instead of the real disk usage. The real usage is
       used in normal runs, so nothing had to be restored.</p>
    <div class="table-container">
      <table>
        <thead>
          <tr><th scope="col">Test input</th><th scope="col">Expected status</th><th scope="col">Actual status</th></tr>
        </thead>
        <tbody>
          <tr><td>50%</td><td>OK</td><td>$(get_disk_status 50)</td></tr>
          <tr><td>80%</td><td>WARNING</td><td>$(get_disk_status 80)</td></tr>
          <tr><td>90%</td><td>WARNING</td><td>$(get_disk_status 90)</td></tr>
        </tbody>
      </table>
    </div>
 
    <h3>Automatic updates</h3>
    <p>I read the generation time from the file twice, about one minute apart:</p>
    <pre>grep "Report generated" /var/www/html/viikko3/index.html</pre>
    <ul>
      <li>1st automatic update: <strong>2026-11-10 16:02:01 EET</strong></li>
      <li>2nd automatic update: <strong>2026-11-10 16:03:01 EET</strong></li>
    </ul>
    <p>The time changed by exactly one minute, so cron runs the script as planned.</p>
 
    <h3>Reboot test</h3>
    <p>I rebooted the VM with <code>sudo reboot</code> on 2026-11-10 at about 16:04 EET.
       After logging back in I checked the situation:</p>
    <pre>&#36; uptime -s
2026-11-10 16:04:42
 
&#36; systemctl is-active nginx mariadb viikko2 cron
active
active
active
active
 
&#36; grep "Report generated" /var/www/html/viikko3/index.html
... 2026-11-10 16:07:01 EET (UTC+02:00) ...</pre>
    <p>The new boot time shows that the reboot happened. Nginx, MariaDB, my Week 2
       application and cron all started automatically. The report was generated
       again after the reboot (16:07:01), so the schedule continued without any
       manual action. Both <code>/viikko2/</code> and <code>/viikko3/</code> opened
       normally in the browser.</p>
  </section>
 
  <section>
    <h2>A problem solved or a lesson learned</h2>
    <p><strong>Problem:</strong> My first command for reading the generation time,
       <code>grep -o "[0-9-]* [0-9:]* UTC" index.html</code>, suddenly printed nothing.
       The reason was that I had changed the server's time zone with
       <code>sudo timedatectl set-timezone Europe/Helsinki</code>, so the page no longer
       said <code>UTC</code> but <code>EET</code>. I solved it by checking the time zone
       with <code>date</code> and using a simpler search, <code>grep "Report generated"</code>,
       which works in any time zone.</p>
    <p><strong>Lesson learned:</strong> To push to GitHub from the server I used a
       <em>deploy key</em>, an SSH key that only has access to this one repository
       instead of my whole GitHub account. Only the public key was added to GitHub;
       the private key stays on the server and is never published. I also checked that
       the host fingerprint shown by <code>ssh -T git@github.com</code> matched
       GitHub's official fingerprint before answering <code>yes</code>.</p>
  </section>
 
  <footer>
    <p><a href="$GITHUB_URL">View the source code on GitHub</a></p>
  </footer>
</body>
</html>
EOF
 
# mktemp creates the file with permissions 600, Nginx needs to read it
chmod 644 "$TEMP_FILE"
mv "$TEMP_FILE" "$OUTPUT_FILE"
 
