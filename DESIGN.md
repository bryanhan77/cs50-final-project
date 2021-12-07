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

-- This table keeps track of all the items that are currently availible for sale. Notice that we store the file as a BLOB data type which stands for Binary Large OBject. 

CREATE TABLE past (id INTEGER, person_id INTEGER, file BLOB, name TEXT NOT NULL, description TEXT NOT NULL, price NUMERIC, category TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(person_id) REFERENCES users(id));

-- This is an indentical table of format to items, but stores only past items that are no longer in the items table. 



HTML
index.html
- we use jinja to loop through the table array and select the correct item dictionaries according to the their category
- 