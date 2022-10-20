# CS50-Final-Project 
December 7, 2021
Harvard College
Bryan Han and Paul Chin
TFs: Coby Sheehan and Varshini Subhash
----------------------------------------

Presentation link: https://youtu.be/xuT1Ok-Dhyc

Welcome to our CS50 Final Project: Harvard Marketplace. Harvard Marketplace is a web app that allows students to upload items they want to sell, buy items other students have listed, and keep track of past purchases and items that you personally have uploaded. We have written the backend in Python/Flask and implemented the web interface in HTML/CSS. The project builds off of many concepts we have learned throughout the year and also explores new concepts such as the use of Jinja and data storage. 

To run the program, make sure you are in the CS50 codespaces where python, SQL, java script, http-server are available. If not, make sure you have these programs downloaded locally per https://www.youtube.com/watch?v=TZ6c7y8N64k&ab_channel=CS50 for mac or https://www.youtube.com/watch?v=9yzQCgIdL-Y&ab_channel=CS50 for windows. 

To test the code, upload the CS50-FINAL-PROJECT folder and change directory to that folder. If you're using the online codespace, make sure you change directory out of the CS50 codesapce (by $cd ..). You can then git clone our repository with the following line: $git clone git@github.com:bryanhan77/CS50-Final-Project.git and then cd into the CS50-Final-Project folder.

Then, run "flask run" in your command line and click on the available server, you should see a link something like: "https://pjchin12-code50-31169723-7w5gp5r92r76r-5000.githubpreview.dev/". The link should open up to the login page where you can register as a new user with your name and password. 
Once doing so, it should bring you to our home page where you can see all the current items listed. Navigate the different available items with the side bar by clicking on the type category you're interested in. Click on the image to see a full screen version of the image. Once you're interested in an item, go ahead and click buy which will bring you to the buy page. Enter your credit card (an example is provided) and your password from before. Great! You've purchased an item! Check in past purchases to see your item, and notice that it is now gone from listings. Now, let's upload an item by clicking sell. That will bring you to a page where you can upload the name of your item, a description, a price, an image, and a category for your item. Once all of the fields have been filled, click "Post Listing". You should now see your item appear on the homepage under the correct category. Check to see your past uploads in the "Your Listings" tab. Once finished, you can logout. 

The project has three main parts: app.py, written in Flask/Python, which is the backend implementation; the templates folder, which contains all of our HTML files; and hmart.db, which contains our tables written in SQL. In this file, we'll talk mainly about app.py, and in styles.md, the templates and databases. You will also notice other relevant files/folders such as helpers.py, requirements.txt, and a static folder - we'll touch on these briefly. Lastly, there are other files/folders such as _pychache_, flask_session, venv, and various sql files that allow the code to run, but are largely irrelevant to our implementation of the project. 

Understanding app.py. 
Open up app.py. Atop the file are a bunch of imports, among them CS50’s SQL module and a few helper functions. 

After configuring Flask, notice how this file disables caching of responses (provided you’re in debugging mode, which you are by default in your code50 codespace), lest you make a change to some file but your browser not notice. Notice next how it configures Jinja with a custom “filter”, usd, a function (defined in helpers.py) that will make it easier to format values as US dollars (USD). It then further configures Flask to store sessions on the local filesystem (i.e., disk) as opposed to storing them inside of (digitally signed) cookies, which is Flask’s default. The file then configures CS50’s SQL module to use hmart.db.

Thereafter are a whole bunch of routes: index, buy, yourlistings, yourpurchases, login, logout, register, and sell. Notice how most routes are “decorated” with @login_required (a function defined in helpers.py). That decorator ensures that, if a user tries to visit any of those routes, he or she will first be redirected to login so as to log in. Let's quickly walk through these functions starting with login and logout which you should be familiar with from Pset 9 (the finance pset). 

When login is called, it uses db.execute to query hmart.db to see if the login username exists. Notice, how it uses check_password_hash to compare hashes of users’ passwords. Finally, notice how login “remembers” that a user is logged in by storing his or her user_id, an INTEGER, in session. That way, any of this file’s routes can check which user, if any, is logged in. Meanwhile, notice how logout simply clears session, effectively logging a user out.

Calling index effectively displays all of the current items in the items database - which is constantly being updated as people buy and sell. We select the entire items table in hmart.db and send this array of dictionaries (where each dictionary represents an item) to index.html when we render index.html. Notice, though, that we must first decode all of the image files from base64 format and update the table with the decoded files. This all done by the decode() function written in helpers.py. This is to eventually allow the image to be read in the <img> html tag. 

When accessing the buy function via get, we render the buy.html page while displaying the pertinent information for the item to-be purchased. This is done by retrieving the id of the item (which is sent as a hidden input in the buy.html), querying for the dictionary associated with that id, and then sending that dictionary to buy.html where the information can be displayed.
When submitting the buy function via post, the user purchases an item by inputting their password and credit card number. If the password is incorrect (check with the password compare hash) or if the credit card is invalid (check with Luhn's algorithm implemented in helpers.py), we throw an error. We then simply update the "items" and "past" tables - deleting the purchased item from items table, and recording the purchased item in "past". 

The yourlistings function queries for all your past listings and passes it to the yourlistings.html file, where it displays all the items you've set up for purchase.

The pastpurchases function queries for all your past purchases and passes it to the yourchases.html. 

The sell function allows you to upload image of an item you want to sell, and requires the user to give its price, a description, and category. The sell function proved to be tricky to implement as we had to figure out how to store the image files. 

------

helpers.py
We retain the apology, login_required, and usd functions from Finance and add our own cc_validate and decode. cc_validate of course comes from Pset 1 (credit). The decode function takes in an array of dictionaries, and updates each of the files in the dictionary with a decoded version of that file. See https://stackoverflow.com/questions/3470546/how-do-you-decode-base64-data-in-python for more information on decoding base64.

requirements.txt
This file simply prescribes the packages on which this app will depend.

static/
Inside static lives styles.css which helps with formatting/layout design in html. You will also the harvard logo (favicon.ico) which is displayed in the tab when the app is run. See header of test.html for implementation.  

---

We talk about the design of html in DESIGN.md. 
