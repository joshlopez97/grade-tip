import json
from bs4 import BeautifulSoup, SoupStrainer, Comment, ProcessingInstruction, Doctype
import unicodedata
import requests
import random
from urllib.parse import urljoin
import re
import traceback

courseregex = r'[A-Z][A-Z0-9&-/(), ]*[A-Z](?: |&nbsp;|\xa0)[A-Z]?[0-9]+[A-Z]?'
# courseregex = r'AMERSTD.{0,2}[0-9]+'
baseURL = "http://guide.berkeley.edu/courses"
target = 'University of California Berkeley'

""" Helper gets all links from webpage """
def getLinks(url):
    return [link['href'] for link in BeautifulSoup(requests.get(url).content,"lxml",parse_only=SoupStrainer('a')).find_all('a', href=True)]

def extractCourses(url):
    # parse text elements from html
    courses = []
    for elem in BeautifulSoup(requests.get(urljoin(baseURL, url)).content, "lxml").findAll('span', attrs={'class': 'code'}):
        if elem.parent.name not in ['script','style'] and all(not isinstance(elem,i) for i in [Comment, ProcessingInstruction, Doctype]):
            courses += re.findall(courseregex, unicodedata.normalize("NFKD", elem.text))
    print(courses)
    return courses

""" Course Scraper for Website """
def getCourses():

    # School URL
    URL = baseURL
    courses = []

    # get all links in page
    links = getLinks(URL)
    for link in links:
        if re.match(r'/courses/.+', link):
            print(link)
            courses += extractCourses(link)

    return courses

""" Load colleges. """
with open('course_catalog.json', 'r') as f:
    college_data = json.load(f)
    start_count = len(college_data)

for college in college_data.keys():
    if college == target:
        college_data[college]['courses'] = getCourses()
        for course in college_data[college]['courses']:
            print(course)


while True:
    change = False
    inspect = input('\n\nEnter a key to inspect, \'random\', or press \'Q\' to quit\n\n> ')
    if inspect in 'qQ \n':
        break
    if inspect.startswith('change '):
        inspect = re.sub('change ', '', inspect)
        change = True
    if inspect == 'random':
        inspect = random.choice(list(college_data.keys()))
    elif inspect.lower() in test_suite:
        inspect = test_suite[inspect.lower()]
    elif inspect.isdigit() and int(inspect) < len(college_data.keys()):
        inspect = cnames[int(inspect)]
    elif inspect.islower():
        inspect = inspect.title()

    inspected_data = college_data.get(inspect)
    if inspected_data:
        if change:
            new_key = input("Enter new key name for {}: ".format(inspect))
            college_data[new_key] = college_data.pop(inspect)
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
        json.dump(college_data, f, indent=2, sort_keys=True)
elif finish == '1':
    print("Saving...")
    with open('course_catalog.json', 'w') as f:
        json.dump(college_data, f, indent=2, sort_keys=True)


