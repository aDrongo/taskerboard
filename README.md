## Taskerboard
### Work in Progress

A simple ticketing system that uses a combination of traditional listing and kanban board styling.

### Install

* Install at least python 3.7  
* Run pipenv install  
* Run init.py or sample.py to initialize the database  
* Run web.py to start the web service  


### Design

web.py                  #Provides website
    static/
        css/            #CSS
        js/             #Javascript
    templates/          #Provides static html pages with Jinja templating
    Modules/
        database.py     #Holds functions to interface with database
            models.py   #Holds models for tables in database
        forms.py        #Holds forms for website, talks to database.py as well
        mail.py         #Holds mail functions
        assorted.py     #functions for trivial usage throughout application
app.db                  #SQLite database
config.json             #Config file


### Completed

1. Database for Tickets, Users and Comments
2. Display to show tickets as a traditional list
3. Display to show tickets as a Kanban board
4. Create and Update tickets
5. API to retrieve, update and create tickets
6. Drag and Drop tickets in Kanban to change status
7. Multiple tags per ticket
8. Ticket Sorting and Filtering
9. Manage Users
10. Search feature
11. Quick editing from list menu
12. CSS Update
13. PyTests
14. Size limit
15. Import/Export database via JSON


### TODO

* Take in emails and send out emails. Can use flask-mail
* Pytests for new features added
* Wiki? Could use Flask-FlatPages
* Due in X time
* LDAP integration?
* Secure API
* Security Review
* Ticket submission portal?
* Chat templating? (Chat assistant?)
* Purchase tracking? (implment this via Category next to Project vs Tickets?)
* Asset tracking?
* Backup database

#### DB Schema Changes required

* User time tracking diary?
* Parent/Child Tickets?
* View Permissions?
* User groups/multiple users per ticket?
* TimeZones?
* Notes vs Comments?
* Attach file to comment/ticket


#### Bugs

Div to quick assign through table doesn't move with scroll. Need JS implementation instead?