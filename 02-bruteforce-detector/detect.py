import re
import csv
from collections import Counter

THRESHOLD = 5  # failed logins from one IP before we raise an alert

counts = Counter()

# read the log and count failed logins per IP
with open('auth.log') as f:
    for line in f:
        if 'Failed password' in line:
            match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
            if match:
                counts[match.group(1)] += 1

# write the report and print alerts
with open('report.csv', 'w', newline='') as out:
    writer = csv.writer(out)
    writer.writerow(['ip', 'failed_logins', 'alert'])
    for ip, total in counts.items():
        alert = 'YES' if total >= THRESHOLD else 'NO'
        writer.writerow([ip, total, alert])
        if total >= THRESHOLD:
            print(f'ALERT: {ip} had {total} failed logins')




