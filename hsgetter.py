import csv
import re

schools = []
with open('hs.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        if not re.match(r'.*(JUNIOR|JR|JR\.)\s*HIGH.*', row[7]) and re.match(r'.*(HIGH|HIGH SCHOOL)$', row[7]):
            if re.match(r'.* HIGH\s*$',row[7]):
                row[7] = row[7].strip() + ' SCHOOL'
            row[7] = re.sub(r'^([^\s]*) - (.*)', r'\2', row[7])
            schools += ["%s (%s, %s)" % (row[7].title(), row[10].title(), row[11].upper())]



with open('secondary_school_list.txt', 'w') as f:
    for school in schools:
        f.write(school + '\n')