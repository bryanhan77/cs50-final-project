app.py
Lines 2-3. Import base64 module to work with the image datatypes. 
Line 45. We use this decode function several times throughout to decode the BLOB files stored in the SQL database. We noticed we were copying a pasting a lot so we instead implemented this function and cut down around 20 lines of code. 
Line 80. We call the cc_validate function written in helpers.py that runs the Luhn's algorithm and validates the credit card. 
Line 81. Notice that the "get" method requires that we use request.args.get() instead of the request.form.get() we typically saw in the "post" method. 
Lines 191-193. First notice we use request.file.get (instead of request.form.get) when accessing the file. We then need to read the file into a variable (data) and render the data into base64 which can then be stored in the BLOB datatype in SQL. We input all the other attributes of the item into the items table. NOTE: WE CAN ONLY UPLOAD PNG FILES. Future directions for this project include figuring out how to enable multiple image file formats. 

Here's the schema of hmart.db. 

CREATE TABLE users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));
CREATE UNIQUE INDEX username ON users (username);

-- The users table stores the account info of all registered users including username and password. 

CREATE TABLE items (id INTEGER, person_id INTEGER, file BLOB, name TEXT NOT NULL, description TEXT NOT NULL, price NUMERIC, category TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(person_id) REFERENCES users(id));

-- This table keeps track of all the items that are currently available for sale. Notice that we store the file as a BLOB data type which stands for Binary Large Object. 

CREATE TABLE past (id INTEGER, person_id INTEGER, file BLOB, name TEXT NOT NULL, description TEXT NOT NULL, price NUMERIC, category TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(person_id) REFERENCES users(id));

-- This is an identical table of format to items, but stores only past items that are no longer in the items table. 


HTML

test.html
- This is the base template from which all other html templates are derived. It should technically be called template.html, but when we were testing it out, we just called it test.html. test.html is adapted from an html template from W3schools, referenced in the test.html file. All html pages import bootstrap, W3schools, and styles.css for various formatting packages. 
- If something seems cryptic, it usually just a stylizing attribute derived from either bootsrap or W3schools. 
- Line 65 allows us to extend test.html
- Line 69-75 allow for full screen display of image.

index.html
- We use jinja to loop through the table array and select the correct item dictionaries according to their category. This allows us to grow and shrink the items that are displayed according to their availibility. 

buy.html
- In lines 37-39, we had to send a hidden form with the value of the item id. This is how we make a "unique" submit button for each item such that when we go to the buy page, we know exactly what item we are purchasing. 

sell.html
- In line 25, we have an input button take an a "file" type where the image can be a png or jpg (image/*).


