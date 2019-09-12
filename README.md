[![GitHub version](https://badge.fury.io/gh/joshlopez97%2Fgrade-tip.svg)](https://badge.fury.io/gh/joshlopez97%2Fgrade-tip)
[![Build Status](https://travis-ci.org/joshlopez97/grade-tip.svg?branch=master)](https://travis-ci.org/joshlopez97/grade-tip)
# GradeTip
## Overview
[GradeTip](https://gradetip.com) is a document-sharing platform and forum for college students. It allows users to create text posts and PDF document posts on their school's GradeTip page. This is to help students gain access to study resources and collaborate with one another.  
## How to run application
### Prerequisites
- Install [Python 3](https://docs.python-guide.org/starting/installation/) and [pip](https://pip.pypa.io/en/stable/installing/)

### Clone the repository and cd into it
```
git clone https://github.com/joshlopez97/grade-tip.git
cd grade-tip/
```

### Install required packages
```
pip3 install -r requirements.txt
```

### Run application
In develop mode:
```
python3 wsgi.py
```
In production mode:
```
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
```
For actual deployment instructions using NGINX, follow the instructions [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04).

## Motivation
The motivation behind this website is to create an affordable service that would serve students better than existing services. Many services similar to this force students to pay a monthly subscription fee for access to documents, along with other caveats. If a student wants access to a certain document, they should be able to do that at a reasonable price. College is expensive enough as is!

## School Data
Using web crawling, this list has compiled a list of all universities and course codes from various Internet sources such as RateMyProfessor and online course catalogs. This information allows autocomplete to suggest school names and course codes in various forms. We've also pulled data from the [Geonames API](http://www.geonames.org/export/web-services.html) to populate GPS coordinates for most of our schools.

## Site Features
### Schools Near You
On the homepage of the site, 5 schools are listed as being "near" the user. First, we ask the user for their browser geolocation. If that is not provided, we estimate the geolocation using their IP address. Using those longitude and latitude coordinates, we can get the 5 closest schools to that user. There is also a downward arrow that generates the next closest 5 schools. 
### Forum
On each school's page in GradeTip, a user can create text posts to interact with that community. This is useful for asking others if they may be able to help with a certain course or provide advice related to that school. Each post allows for community interaction in the form of likes and replies. All text posts and replies must be approved by a moderators before they are made public on GradeTip.
### Uploads
Each PDF file that is uploaded is first converted to images, and then a preview image is extracted from those images. The preview image is comprised of the first page in the PDF with the top 50% of the image blurred out. This is what users will see when looking at the post before they are granted access.
The user that uploaded the image is able to grant access to anyone that requests access. Soon, this will be in the form of payment where two students will essentially be completing a transaction between each other for access to the document.
### Content Monitoring
Since GradeTip is inherently a fairly anonymous platform, it's important to incorporate strong content moderation to avoid unwanted content that would damage the reputation of the site. To do this, we've incorporated a content monitoring page where admin users can approve or deny requests to create various types of content.
### Academic Integrity and Legal Issues
GradeTip is meant for the exchange of documents and knowledge that are legally allowed to be shared and are not violating any school's academic integrity policies. Any content that is found to be another person's intellectual property, violates copyright, or is otherwise in violation of our [Terms of Service](https://gradetip.com/terms) will be removed immediately.
