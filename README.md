# Elevator Maintenance Company (EMC) Django Web Application

## Distinctiveness and Complexity:
With this project, I tried to answer a real life request. I learned that an elevator maintenance, repair and installation company, where my brother also works, needed a web application to manage their teams and monitor their areas of responsibility. So I decided that as the final project of the CS50x, I could address this issue and find a solution to their needs.

So here is the list, hope it'll help:

- Template files are for registration, login, adding building, listing all buildings, building details, creating team, listing all teams, creating tasks, listing all tasks etc.
- JS files for doing some single page app actions.
- models.py for my database models
- urls.py for my app's urls
- views.py contains python functions for my app
- admin.py contains authentication configurations for admin users
- db.sqlite3 is my database
- requirements.txt contains libs and modules used in this project
- README.md file is this file
- wstyles.css is my stylesheet
- .gitignore for ignoring some files during git commit


## Brief summary of the project:
The company wanted to:
 - keep records for the buildings with which they had a maintenance and repair agreement, 
 - to create tasks for the elevator maintenance of the buildings they had contracted with, 
 - and to follow up the results of the tasks by assigning these tasks to teams. 
 - The teams who took their daily duties wanted to visit all the buildings by following a suitable route through the application. 

## What has been done?
1. A personnel authorized by the company was allowed to record their information about the buildings with which an elevator maintenance/repair agreement was made, via the web application.
2. It was ensured that a personnel authorized in the company could form maintenance/repair teams and assign a team leader and sufficient number of employees to these teams.
3. A personnel authorized in the company can create maintenance/repair tasks related to the buildings added to the database and assign these tasks to previously created maintenance/repair teams.
4. When the staff working in the teams visited the developed web application, it was ensured that they could see the tasks assigned to the team they belonged to. In addition, it was possible to view the all tasks -which are need to be completed- combined driving route with a single touch, by creating the most appropriate driving route, on the Yandex Maps web page or the Yandex Maps mobile application.
5. Teams can mark tasks as “Completed” which are done.
6. It has been ensured that all daily tasks can be followed by a personnel assigned at the company headquarters.
7. Completed, ongoing and canceled missions related to past missions can be viewed.
8. Adding/removing employees to the created teams is possible.
9. Team and building informations can be updated.
10. It has been ensured that company employees make the first registration themselves, but these employees are prevented from accessing the system before they are approved by the company HQ.

## How does it work?
1. First, install the requirements in the requirements.txt file.
2. Then run it with the command 
    ```sh
    python manage.py runserver
    ```
3. Superuser => 
    username: Sercan
    pass:1234

## Things to know:
1. Several buildings, teams and users have already been added to the database.
2. Since the company that needs this web application is located in Eskişehir, Turkey, API settings have been made to focus on the relevant region when it is desired to create a route for the tasks. (When you add a building address with another city or country address, the focus of the map will be Eskişehir, even if the route is created.)
3. DATABASE: SQLite
4. Some inline and seperated JS used
5. To create a drive route I got an Yandex Geocoder API KEY and this way whenever a new building added to databease, I simply send the address and get the Lon. Lat. coordinates and store them in database. This way, an employee can easily create drive route for all his assigned tasks.

THANK YOU FOLKS!
