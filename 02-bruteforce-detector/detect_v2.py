import re
import csv
from datetime import datetime

LIMIT = 5            # failures needed to raise an alert
WINDOW_SECONDS = 60  # ...inside this many seconds
YEAR = 2026          # the log has no year, so we add one

# Step 1: collect the time of every failed login, per IP
failures = {}

with open('auth_v2.log') as log_file:
    for line in log_file:
        if 'Failed password' not in line:
            continue

        found = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
        if found is None:
            continue
        ip = found.group(1)

        # The first 15 characters of the line are the time, like "Oct 10 10:00:01"
        when = datetime.strptime(f'{YEAR} {line[:15]}', '%Y %b %d %H:%M:%S')

        if ip not in failures:
            failures[ip] = []
        failures[ip].append(when)

# Step 2: for each IP, find the busiest window and write the report
with open('report_v2.csv', 'w', newline='') as report_file:
    writer = csv.writer(report_file)
    writer.writerow(['ip', 'total_failures', 'most_in_window', 'alert'])

    for ip, times in failures.items():
        times.sort()
        most_in_window = 0

        # Start a window at each failure and count how many fall inside it
        for start in times:
            count = 0
            for t in times:
                seconds_later = (t - start).total_seconds()
                if 0 <= seconds_later <= WINDOW_SECONDS:
                    count += 1
            if count > most_in_window:
                most_in_window = count

        if most_in_window >= LIMIT:
            alert = 'YES'
            print(f'ALERT: {ip} had {most_in_window} failed logins within {WINDOW_SECONDS} seconds')
        else:
            alert = 'NO'
        writer.writerow([ip, len(times), most_in_window, alert])
