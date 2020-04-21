# Live project link
http://bradington.pythonanywhere.com/


# Project Overview

A web app designed to solve the disjointed processes at my employer,
a manufacturer of protein bars.



The app will provide a single reference point for all interconnected activities.


# Problem (s) to solve

1. Customer details are stored in Word files, excel documents and other apps.
2. Each customer has a list of recipes for their products, but these recipes are kept in seperate folders.
3. There's no analytics for: 
 - the amount of recipes created for each customer
 - the number of orders completed
 - the number of products produced across all customers
4. Recipes are created manually using Excel
 - Ingredients and nutritional information has to be added manually to each new recipe
 - No consistency between Excel sheets
 - Formulas are prone to human error
 - Inconsistant recipes are causing issue for buying team - they're either over or under ordering stock
5. Stock control is inconsitant:
 - Currently using Sage to track stock which doesn't allow for multi-site stock control
 - No batch traceability for stock items
 


# Solutions / Functions

1. User registration and login
2. User overview / dashboard page of existing jobs, no. customers, scheduled work for the week, notice board
3. Customer dashboard
 - Add / delete / edit customers
 - See number of jobs completed
 - No. of recipes
 - Value of customer
4. Ingredient list / nutritional creator
 - Database to store list of ingredients and corresponding nutritional values
 - Ability to see full list / select by type
 - Ability to add / remove ingredients
 - Ability to upload excel sheet of ingredients
 - Ability to edit existing ingredients
5. Recipe creator
 - Create recipe and store for each customer
 - Can only use data from ingredients database
 - Ability to edit existing recipes
 - Automatically works out nutritional information per 100g and product weight

# Technology Expectations
1. Front-end
 - Html
 - CSS
 - Bootstrap
 - Javascript / Jquery
 - Ajax

2. Backend
 - Flask / Python
 - SqLite


# Bugs to fix
1. ~~Navigation dropdown menu off screen.~~
2. ~~Password validation on login~~
3. ~~Order info page error on refresh (session isn't working)~~
        

