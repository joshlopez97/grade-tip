import json
with open('course_catalog.json', 'r') as f:
    college_data = json.load(f)
with open('secondary_school_list.txt', 'r') as f:
    hsdata = [line.strip('\n') for line in f if line.strip('\n')]