# Credit Cards!

Hiya, and welcome to Credit Cards. The purpose of this application is to get a job at Albert. But it also does cool stuff!
Like:
- validate existing credit card numbers and
- generate new ones, given a one or two digit Issuer Identification Number.

Now, on to how to set it up.

## Installation
To install Credit Cards, you'll need a computer with pip and Python >3.7 installed. I'm assuming in the instructions that
you're using a macintosh computer.

You can optionally start by creating a virtual environment and activating it:
```
virtualenv .venv
source .venv/bin/activate
```

This will keep all the dependencies from this project separate from your system dependencies. That's good for the soul.
Next, install the project dependencies:
```
pip3 install -r requirements.txt
```

Because Django includes relational database models, to get the tests to run you'll need to run:
```
python manage.py makemigrations
python manage.py migrate
```

If you want to be thorough, you can run the provided test cases with the following command:
```
python manage.py test api
```
Which should hopefully read nine test cases passed.

To start the app, run:
```
python manage.py runserver
```
And navigate to http://localhost:8000/api to see the landing page.

## Validate
The format of the URL for the validate function looks like:
---
http://localhost:8000/api/validate?number=<your_number_here>
---
Where `<your_number_here>` gets replaced with the credit card number you'd like to validate. If the number is valid,
you'll get back a JSON object with:
- Whether the number is valid
- The Major Industry Identifier
- The Issuer Identification Number
- The Personal Account Number
- The Check Digit

If the card number is not valid, you'll get back a similar response, but all of the attributes other than is_valid
will be set to null. Try it out and see what you think!

## Generate
Similar to validate, the format of the URL looks like:
---
http://localhost:8000/api/generate?iin=<your_iin_here>
---
Where `<your_iin_here>` gets replaced with the Issuer Identification Number you'd like your generated card number to
start with. If the IIN is valid, you'll get back a JSON object with the same information as a valid call to validate,
except the card number you get will be completely random :0 Otherwise, you'll get back an error message:
```
{"error": "IINs should be only digits and either length one or two. Try 65!"}
```