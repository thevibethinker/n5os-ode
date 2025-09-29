import csv
import datetime
from datetime import timezone, timedelta

cutoff = datetime.datetime.now(timezone.utc) - timedelta(days=3)

rows = []
with open('/home/workspace/jobs_aggregation_2025-09-22.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    header.append('Within_3_Days')
    rows.append(header)
    for row in reader:
        day_str = row[0]
        try:
            day = datetime.datetime.strptime(day_str, '%Y-%m-%d')
            day = day.replace(tzinfo=timezone.utc)
        except Exception:
            day = None
        if day and day >= cutoff:
            row.append('yes')
        else:
            row.append('no')
        rows.append(row)

with open('/home/workspace/jobs_aggregation_2025-09-22.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
