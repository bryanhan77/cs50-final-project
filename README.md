# CS50-Final-Project
This documentation is to be a user’s manual for your project. Though the structure of your documentation is entirely up to you, it should be incredibly clear to the staff how and where, if applicable, to compile, configure, and use your project. Your documentation should be at least several paragraphs in length. It should not be necessary for us to contact you with questions regarding your project after its submission. Hold our hand with this documentation; be sure to answer in your documentation any questions that you think we might have while testing your work.

Welcome to our CS50 final project: H-Mart. H-Mart is a web app that allows studets to upload items they want to sell, buy items other students have listed, and keep track of past purchases and items that you personally have uploaded. We have written the backend in python/flask and implemented the web interface in html. The project builds off of many concepts we have learned throughout the year from databases to dictionaries, but also explores new concepts such as file upload and data storage. 

The project has three main parts: app.py, written in flask/python, which is the backend implementation; the templates folder, which contains all of our html files; and hmart.db, which contains our tables written in sql. In this file, we'll talk mainly about app.py, and in styles.md, the templates and databases. You will also notice other relevant files/folders such as helpers.py, requirements.txt, and a static folder - we'll touch on these briefly. Lastly, there are other files/folders such as _pychache_, flask_session, venv, and various sql files that allow the code to run, but are largely irrelevant to our implementation of the project. 

Understanding app.py. 
Open up app.py. Atop the file are a bunch of imports, among them CS50’s SQL module and a few helper functions. 

After configuring Flask, notice how this file disables caching of responses (provided you’re in debugging mode, which you are by default in your code50 codespace), lest you make a change to some file but your browser not notice. Notice next how it configures Jinja with a custom “filter,” usd, a function (defined in helpers.py) that will make it easier to format values as US dollars (USD). It then further configures Flask to store sessions on the local filesystem (i.e., disk) as opposed to storing them inside of (digitally signed) cookies, which is Flask’s default. The file then configures CS50’s SQL module to use hmart.db.

Thereafter are a whole bunch of routes: index, buy, yourlistings, yourpurchases, login, logout, register, and sell. Notice how most routes are “decorated” with @login_required (a function defined in helpers.py). That decorator ensures that, if a user tries to visit any of those routes, he or she will first be redirected to login so as to log in. Let's quickly walk through these functions starting with login and logout which you should be familiar with from Pset 9 (the finance pset). 

When login is called, it uses db.execute to query hmart.db to see if the login username exists. Notice, how it uses check_password_hash to compare hashes of users’ passwords. Finally, notice how login “remembers” that a user is logged in by storing his or her user_id, an INTEGER, in session. That way, any of this file’s routes can check which user, if any, is logged in. Meanwhile, notice how logout simply clears session, effectively logging a user out.

Calling index effectively displays all of the current items in the items database - which is constantly being updated as people buy and sell. We select the entire items table in hmart.db and send this array of dicitionaries (where each dictionary represents an item) to index.html when we render index.html. Notice, though, that we must first decode all of the image files from base64 format and update the table with the decoded files. This all done by the decode() function written in helpers.py. This is to evnetually allow the image to be read in the <img> html tag. 

When accessing the buy function via get, we render the buy.html page while displaying the pertinent information for the item to-be purchased. This is done by retrieving the id of the item (which is sent as a hidden input in the buy.html), querying for the dictionary associated with that id, and then sending that dictionary to buy.html where the information can be displayed.
When submitting the buy function via post, the user purchases an item by inputting their password and creditcard number. If the passwrord is incorrect (check with the password compare hash) or if the credit card is invalid (check with Luhn's algorithm implemented in helpers.py), we throw an error. We then simply update the "items" and "past" tables - deleting the purchased item from items table, and recording the purchased item in "past". 

The yourlistings function queries for all your past listings and passes it to the yourlistings.html file, where it displays all the itmes you've set up for purchase.

The pastpurchases fucntion queries for all your past purchases and passes it to the yourchases.html. 

The sell function allows you to upload image of an item you want to sell, and requires the user to give its price, a description, and category. The sell function proved to be tricky to implement as we had to figure out how to store the image files. 

------

helpers.py
We retain the apology, login_required, and usd functions from Finance and add our own cc_validate and decode. cc_validate of course comes from Pset 1 (credit). The decode function takes in an array of dictionaries, and updates each of the files in the dictionary with a decoded version of that file. See https://stackoverflow.com/questions/3470546/how-do-you-decode-base64-data-in-python for more information on decoding base64.

---

We talk about most of the design of html in style.md. We mention here, though, that test.html is the base template from which all other html templates are derived. It should technically be called template.html, but when we were testing it out, we just called it test.html. test.html is adapted from an html template from W3schools, referenced in the test.html file. All html pages import bootstrap, W3schools, and styles.css for various formatting packages. 













