import json
from bs4 import BeautifulSoup
from collections import defaultdict
import random
import requests
import re
import traceback

""" Load colleges. """
with open('course_catalog2.json', 'r') as f:
    college = json.load(f)
    start_count = len(college)

""" Load high schools. """
# with open('secondary_school_list.txt', 'r') as f:
#     hs = [line.strip('\n') for line in f if line]

""" Static helper info. """
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
test_suite = {"uci": "University of California Irvine", "dvc": "Diablo Valley College", "ucla": "University of California Los Angeles", "harvard": "Harvard University"}
url = "http://www.geonames.org/search.html?q={}&startRow={}"
examine = 'n'

def normalize(term):
    return re.sub(r' {2,}', ' ', re.sub(r'[^a-z ]','',term.lower()))

def abbreviate(term):
    stopwords = ['of','at','and','the','for']
    return ''.join(re.findall(r'\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w)',term)).lower()

def convertGPS(coords):
    gps = (re.findall(r'\d+',coords[0]),re.findall(r'\d+',coords[1]))
    lat = float(gps[0][0])
    lat += float(gps[0][1]) / 60
    lat += float(gps[0][2]) / 3600
    if coords[0][0] == 'S':
        lat *= -1

    lon = float(gps[1][0])
    lon += float(gps[1][1]) / 60
    lon += float(gps[1][2]) / 3600
    if coords[1][0] == 'W':
        lon *= -1

    return (lon, lat)

def merge_schools(school1, school2):
    college[school1]['courses'] += college[school2]['courses']
    college.pop(school2, None)

def get_results(query):
    for i in range(0,10000,50):
        res = requests.get(url.format(query,i))
        soup = BeautifulSoup(res.content, "lxml")
        trs = soup.find("table",{"class":"restable"})
        if not trs:
            break
        trs = trs.findAll("tr")
        for tr in trs:
            links = tr.findAll("a")
            if links:
                for link in links:
                    test = normalize(link.text.strip())
                    match = translator.get(test)
                    options = abbr.get(test)
                    if match:
                        print("{} <-- {}".format(match, link.text.strip()))
                    elif options:
                        match = options[0]
                        if len(options) > 1:
                            print('Which school best matches {}?\n0.) Skip this school'.format(link.text.strip()))
                            for i, school in enumerate(options):
                                print('{}.) {}'.format(i, school))
                            choice = int(input('> '))
                            if choice == 0:
                                continue
                            match = options[choice]
                        print("{} <-- {} (***)".format(match, link.text.strip()))
                    else:
                        continue
                    gps = [coord.text for coord in tr.findAll("td",{"nowrap":True})]
                    if len(gps) == 2:
                        gps = convertGPS(gps)
                    print(gps)
                    college[match]['lon'] = gps[0]
                    college[match]['lat'] = gps[1]
                    modified[match] = college[match]




""" Perform action. """
print("\n\nStarting...\n\n")
modified = {}
cnames = list(college.keys())

translator = {}
abbr = defaultdict(list)

for i,c in enumerate(cnames):
    try:
        translator[normalize(c)] = c
        abbr[abbreviate(c)] += [c]
    except Exception as e:
        traceback.print_exc()
        cont = input("\n\nError occured while parsing {}, and {} schools modified so far, continue? (y/n)\n\n> ".format(c, len(modified)))
        if cont == 'n':
            exit(0)
get_results('diablo+valley+college')

""" Print modified keys. """
print('\n\nVerifying...\n\n')
if len(college) != start_count:
    print("\n!!! WARNING: length of dictionary has changed from {} to {} !!!\n".format(start_count, len(college)))
for c,v in modified.items():
    print("{}, {} courses".format(c,len(v['courses'])))
if not modified:
    examine = input('\n\nNothing done...or modified not updated. Want to print out the data? (y/n)\n\n> ')
    if examine == 'y':
        i = 0
        for c, v in college.items():
            print("{}.) {}, ({})".format(i,c,len(v['courses'])))
            i += 1

""" Inspect data for desired results. """
if modified or examine == 'y':
    while True:
        change = False
        inspect = input('\n\nEnter a key to inspect, \'random\', or press \'Q\' to quit\n\n> ')
        if inspect in 'qQ \n':
            break
        if inspect.startswith('change '):
            inspect = re.sub('change ', '', inspect)
            change = True
        if inspect == 'random':
            inspect = random.choice(list(college.keys()))
        elif inspect.lower() in test_suite:
            inspect = test_suite[inspect.lower()]
        elif inspect.isdigit() and int(inspect) < len(cnames):
            inspect = cnames[int(inspect)]
        elif inspect.islower():
            inspect = inspect.title()

        inspected_data = college.get(inspect)
        if inspected_data:
            if change:
                new_key = input("Enter new key name for {}: ".format(inspect))
                college[new_key] = college.pop(inspect)
            else:
                print(json.dumps(inspected_data, indent=2))
                print("\n\nShowing data for \"{}\"".format(inspect))

""" Finish process and save. """
finish = input("\n\nProcess finished. Would you like to:"
               "\n\t1 – save to existing file"
               "\n\t2 – save to new file"
               "\n\tENTER – don't save\n\n> ")


if finish == '2':
    print("Saving...")
    with open('course_catalog2.json', 'w') as f:
        json.dump(college, f, indent=2, sort_keys=True)
elif finish == '1':
    print("Saving...")
    with open('course_catalog.json', 'w') as f:
        json.dump(college, f, indent=2, sort_keys=True)
