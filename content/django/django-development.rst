Django 学习
##################################################

:date: 2022-01-01 00:28
:modified: 2022-01-01 00:28
:tags: django

1. Introduction to Django
==================================================

Scaffolding a Django Project and App
--------------------------------------------------

常用命令::

    $ django-admin.py startproject myprojectname .
    $ python manage runserver
    $ python manage startapp myappname

Model View Template
--------------------------------------------------

Models
    Django models define the data for your application and provide an 
    abstraction layer to SQL database access through an Object 
    Relational Mapper (ORM).

Views
    A Django view is where most of the logic for your application is 
    defined. A view is a function that you write that will receive 
    a request in the form of a Python object (specifically, a Django 
    HttpRequest object).Your view must return an HttpResponse object 
    that encapsulates all the information being provided to the client.

Templates
    A template is a HyperText Markup Language (HTML) file (usually – 
    any text file can be a template) that contains special placeholders 
    that are replaced by variables your application provides. 

Introduction to HTTP
--------------------------------------------------

Processing a Request
--------------------------------------------------

#. Match request against URL Routes  -- Django
#. Call view method with HttpRequest Object  -- Your Code
#. Perform logic inside view method   -- Your Code
#. Return HttpResponse object  -- Your Code
#. Send response to client  -- Django

Django Project
--------------------------------------------------

manage.py
    As the name suggests, this is a script that is used to manage your 
    Django project. some of the more common ones are listed here:

    * runserver
    * startapp
    * shell
    * dbshell
    * makemigrations
    * migrate
    * test

The myproject Directory
    This is the actual Python package for your project. It contains 
    settings for the project, some configuration files for your web 
    server, and the global URL maps. 

Django Development Server
    By default, the server listens on port 8000 on localhost (127.0.0.1).

    ::

        python3 manage.py runserver 8001
        python3 manage.py runserver 0.0.0.0:8000

Django Apps
--------------------------------------------------

An app directory contains all the models, views, and templates (and more) 
that they need to provide application functionality. ::

    python3 manage.py startapp myapp

Inside the app directory are several files and a folder :

* __init__.py
* admin.py
* apps.py
* models.py
* migrations
* tests.py
* views.py

View Details
--------------------------------------------------

URL Mapping Detail
--------------------------------------------------

GET, POST, and QueryDict Objects
--------------------------------------------------

Django automatically parses these parameter strings into QueryDict objects. 
The data is then available on the HttpRequest object that is passed to your 
view—specifically, in the HttpRequest.GET and HttpRequest.POST attributes, 
for URL parameters and body parameters respectively. QueryDict objects are 
objects that mostly behave like dictionaries, except that they can contain 
multiple values for a key. Code snippets ::

    qd = QueryDict('k=a&k=b&k=c')
    qd[k']
    qd.get('k')
    qd.getlist('k')

Exploring Django Settings
--------------------------------------------------

Django has more settings available that aren't listed in the settings.py file, 
and so it will use its built-in defaults in these cases. You can also use the 
file to set arbitrary settings that you make up for your application. 
Third-party applications might want settings to be added here as well. 

Using Settings in Your Code ::

    from django.conf import settings # import settings from here instead

    if settings.DEBUG:
        do_some_logging()

When importing settings from django.conf, Django mitigates the three issues 
we just discussed:

* Settings are read from whatever Django settings file has been specified.
* Any default settings values are interpolated.
* Django takes care of parsing any settings defined by a third-party library.

Finding HTML Templates in App Directories
--------------------------------------------------

Django will look in this (and in other apps' templates directories) because of 
APP_DIRS being True in the settings.py file

Rendering a Template with the render Function
--------------------------------------------------

render takes at least two arguments: the first is always the request that was 
passed to the view, and the second is the name/relative path of the template 
being rendered. We will also call it with a third argument, the render context 
that contains all the variables that will be available in the template

Rendering Variables in Templates
--------------------------------------------------

To render a variable in a template, simply wrap it with braces: {{ book_name }}. 
Django will automatically escape HTML in output so that you can include special 
characters (such as < or >) in your variable without worrying about it garbling 
your output. If a variable is not passed to a template, Django will simply render 
nothing at that location, instead of throwing an exception.

Debugging and Dealing with Errors
--------------------------------------------------

Exceptions
    Exceptions are raised (or thrown in other languages) when an error occurs.
    Some common exceptions that you might see:

    * IndentationError
    * SyntaxError
    * NameError
    * KeyError
    * IndexError
    * TypeError

Debugging

Summary
--------------------------------------------------

This chapter was a quick introduction to Django. You first got up to speed on the 
HTTP protocol and the structure of HTTP requests and responses. We then saw how 
Django uses the MVT paradigm, and then how it parses a URL, generates an HTTP request, 
and sends it to a view to get an HTTP response. We scaffolded the Bookr project 
and then created the reviews app for it. We then built two example views to illustrate 
how to get data from a request and use it when rendering templates. You should have 
experimented to see how Django escapes output in HTML when rendering a template.

2. Model and Migrations
==================================================

Django ORM
--------------------------------------------------

Database Configuration and Creating Django Applications
------------------------------------------------------------

Django Apps
--------------------------------------------------

A Django project can have multiple apps that often act as discrete entities. 
That's why, whenever required, an app can be plugged into a different Django project as well. 

Django Migration
--------------------------------------------------

the transformation of Python code into database structures is known as migration. ::

    python manage.py migrate

Creating Django Models and Migrations
--------------------------------------------------

A Django model is essentially a Python class that holds the blueprint 
for creating a table in a database. The models.py file can have many such models, 
and each model transforms into a database table. The attributes of the class form 
the fields and relationships of the database table as per the model definitions.

Field Types
--------------------------------------------------

Field Options
--------------------------------------------------

Django has many more field types and field options that can be explored from the extensive 
official Django documentation. Execute the following command in the shell or terminal to 
migrate the Django models into the database ::

    python manage.py makemigrations appname

The makemigrations <appname> command creates the migration scripts for the given app;
When we run makemigrations without the app name, the migration scripts will be created 
for all the apps in the project. The following command, when run in the shell or terminal, 
will show the status of model migrations throughout the project ::

    python manage.py showmigrations

Next, let's understand how Django transforms a model into an actual database table ::

    python manage.py sqlmigrate appname migrationscript

Primary Keys
--------------------------------------------------

Since the migration script has already been created by executing makemigrations, 
let's now migrate the newly created model in the app by executing the following command ::

    python manage.py migrate app

Relationships
--------------------------------------------------

Many to One ::

    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

Many to Many ::

    contributors = models.ManyToManyField('Contributor', through='BookContributor')

through: This is a special field option for many-to-many relationships. When we 
have a many-to-many relationship across two tables, if we want to store some extra 
information about the relationship, then we can use this to establish the relationship 
via an intermediary table. When the through field option is not provided while 
establishing a many-to-many relationship, Django automatically creates an intermediary 
table to manage the relationship.

One-to-One Relationships ::

    person = models.OneToOneField(Person, on_delete=models.CASCADE)

Model Methods
--------------------------------------------------

In Django, we can write methods inside a model class. These are called model methods and 
they can be custom methods or special methods that override the default methods of Django models. 
One such method is __str__(). This method returns the string representation of the Model instances 
and can be especially useful while using the Django shell. 

Django's Database CRUD Operations
--------------------------------------------------

To execute the CRUD operations, we will enter Django's command-line shell 
by executing the following command::

    python manage.py shell

Exercise 2.02: Creating an Entry in the Bookr Database
    In this exercise, you created an entry in the database by creating an instance of the model object 
    and used the save() method to write the model object into the database. the changes(update) to the 
    class instance are not saved until the save() method is called. 

Exercise 2.03: Using the create() Method to Create an Entry
    Invoke the create() method to create an object in the database in a single step. 
    Ensure that you pass all the required parameters

Exercise 2.04: Creating Records for a Many-to-One Relationship
    In this exercise, we learned that while creating a database record, an object can be assigned to 
    a field if it is a foreign key. 

Exercise 2.05: Creating Records with Many-to-Many Relationships
    use the relationship to create the objects, we can use through_default to pass 
    in a dictionary with the parameters defining the required fields. 

Exercise 2.07: Using the get() Method to Retrieve an Object
    In this exercise, we learned how to fetch a single object using the get() method. 
    There are several disadvantages to using this method, though. It is important to 
    note that the get() method can only fetch one object. If there is another object 
    carrying the same value as the field mentioned, then we can expect a 'returned 
    more than one' error message. We can also get a 'matching query does not exist' 
    error message when there are no objects returned from the get() query. The get() 
    method can be used with any of the object's fields to retrieve a record. 

Exercise 2.08: Using the all() Method to Retrieve a Set of Objects
    In this exercise, we learned how to retrieve all the objects using the all() method 
    and we also learned how to use the retrieved set of objects as a list.

Exercise 2.09: Using the filter() Method to Retrieve Objects
    In this exercise, we saw the use of filters to retrieve a set of a few objects 
    filtered by a certain condition.  Now, let's suppose we want to filter and query 
    a set of objects using the object's fields by providing certain conditions. In such 
    a case, we can use what is called a double-underscore lookup( __gt, __gte,  __lt, __lte, 
    __contains, __icontains, __startswith, etc). 

    we can use the exclude() method to exclude a certain condition and fetch all the required objects. 

    We can retrieve a list of objects while ordering by a specified field, using the order_by() method. 
    We can also use a prefix with the negative sign for the field parameter to order results 
    in descending order. 

    Yet another useful method offered by Django is values(). It helps us get a query set of 
    dictionaries instead of objects. 

Now let's study how to perform queries across relationships. There are several ways 
to go about this, such as Querying Using Foreign Keys, Querying Using Model Name 
(written in lowercase) , Querying Across Foreign Key Relationships Using the Object Instance.

Exercise 2.10: Querying Across a Many-to-Many Relationship Using Field Lookup
    In this exercise, we learned how to perform queries across many-to-many relationships 
    using field lookup.

Exercise 2.11: A Many-to-Many Query Using Objects

Exercise 2.12: A Many-to-Many Query Using the set() Method

Exercise 2.13: Using the update() Method

Exercise 2.14: Using the delete() Method

Summary
--------------------------------------------------

we learned about Django models, migrations, and how they help propagate the changes 
to the Django models in the database.

We shored up our knowledge of databases by learning about database relationships, 
and their key types, in relational databases.  We also worked with the Django shell, 
where we used Python code to perform the same CRUD queries we performed earlier using SQL. 
Later, we learned how to retrieve our data in a more refined manner using pattern matching 
and field lookups.

3. URL Mapping, Views, and Templates
==================================================

4. Introduction to Django Admin
==================================================

Creating a Superuser Account
--------------------------------------------------

Enter the following command to create a superuser::

    python manage.py createsuperuser

Visit the admin app at http://127.0.0.1:8000/admin and log in with the superuser account 
that you have created.

CRUD Operations Using the Django Admin App
--------------------------------------------------

Users and Groups
--------------------------------------------------

Summary
--------------------------------------------------

In this chapter, we saw how to create superusers through the Django command line 
and how to use them to access the admin app. After a brief tour of the admin app's 
basic functionality, we examined how to register our models with it to produce a 
CRUD interface for our data.

Then we learned how to refine this interface by modifying site-wide features. We 
altered how the admin app presents model data to the user by registering custom 
model admin classes with the admin site. This allowed us to make fine-grained 
changes to the representation of our models' interfaces. These modifications 
included customizing change list pages by adding additional columns, filters, 
date hierarchies, and search bars. We also modified the layout of the model admin pages 
by grouping and excluding fields.

5. Serving Static Files
==================================================

Django provides tools for serving static assets with its development server 
during development. When your application goes to production, it can also 
collect all your assets and copy them to a folder for a dedicated web server 
to host. This allows you to keep your static files segregated in a meaningful way 
during development and automatically bundle them for deployment.

This functionality is provided by Django's built-in staticfiles app. It adds 
several useful features for working with and serving static files:

*   The static template tag to automatically build the static URL for an asset and 
    include it in your HTML.
*   A view (called static) that serves static files in development.
*   Static file finders to customize where assets are found on your filesystem.
*   The collectstatic management command, which finds all static files and moves 
    them into a single directory for deployment.
*   The findstatic management command, which shows which static file on disk is 
    loaded for a particular request. This also helps to debug if a particular file 
    is not being loaded.

6. Forms
==================================================

What is a form?
--------------------------------------------------

A form is made up of inputs that define key-value pairs of data to submit to the server.
Each input in the form has a name, and this is how its data is identified on the server-side 
(in a Django view). There can be multiple inputs with the same name, whose data is available 
in a list containing all the posted values with this name.


FORM SECURITY WITH CROSS-SITE REQUEST FORGERY PROTECTION 

The CSRF token must be added into the HTML for every form being sent and is done with 
the {% csrf_token %} template tag. The CSRF token is unique to every visitor on the site 
and periodically changes.

ACCESSING DATA IN THE VIEW

These are request.GET , which contains parameters passed in the URL, and request.POST , 
which contains parameters in the HTTP request body.

* All values are sent as text, even number and date inputs.
* For the select inputs, the selected value attributes of the selected options are sent, 
  not the text content of the option tag.
* If you select multiple options for books_you_own , then you will see multiple values 
  in the request. This is why we use the getlist method since multiple values are sent 
  for the same input name.
* If the checkbox was checked, you will have a checkbox_on input in the debug output. 
  If it was not checked, then the key will not exist at all (that is, there is no key, 
  instead of having the key existing with an empty string or None value).
* We have a value for the name submit_input , which is the text Submit Input . You submitted 
  the form by clicking the Submit Input button, so we receive its value. Notice that no value 
  is set for the button_element input since that button was not clicked.

CHOOSING BETWEEN GET AND POST

* The most important is deciding whether or not the request should be idempotent.
* Another point to consider is that Django only applies CSRF projection to POST requests.
* If sending form data with a GET request, the form parameters will be visible in the URL.
* the maximum length of a URL allowed by a browser can be short compared to the size of 
  a POST body – sometimes only around 2,000 characters (or about 2 KB) compared to 
  many megabytes or gigabytes that a POST body can be

WHY USE GET WHEN WE CAN PUT PARAMETERS IN THE URL?

THE DJANGO FORMS LIBRARY

The Django Forms library allows you to quickly define a form using a Python class.
This is done by creating a subclass of the base Django Form class. You can then use
an instance of this class to render the form in your template and validate the input
data.

DEFINING A FORM

You define a class that inherits from the django.forms.Form class. The class has 
attributes, which are instances of different django.forms.Field subclasses.

When rendered, the attribute name in the class corresponds to its input name in HTML.
To give you a quick idea of what fields there are, some examples are CharField ,
IntegerField , BooleanField , ChoiceField , and DateField . Each field
generally corresponds to one input when rendered in HTML, but there's not always
a one-to-one mapping between a form field class and an input type. Form fields are
more coupled to the type of data they collect rather than how they are displayed.

To illustrate this, consider a text input and a password input. They both accept
some typed-in text data, but the main difference between them is that the text
is visibly displayed in a text input, whereas with a password input the text is
obscured. In a Django form, both of these fields are represented using CharField .
The difference in how they are displayed is set by changing the widget the
field is using.

Django defines a number of Widget classes that define how a Field should be
rendered as HTML. They inherit from django.forms.widgets.Widget . A
widget can be passed to the Field constructor to change how it is rendered.

RENDERING A FORM IN A TEMPLATE

Django does not add the <form> element or submit button(s) for you when
rendering the template; you should add these around where your form is placed in
the template. The form can be rendered like any other variable.

VALIDATING FORMS AND RETRIEVING PYTHON VALUES

We will now look at the other part of what makes Django forms useful: 
their ability to automatically validate the form and then retrieve native Python objects 
and values from them.

In Django, a form can either be unbound or bound. These terms describe whether or
not the form has had the submitted POST data sent to it for validation.A form is bound 
if it is called with some data to be used for validation, such as the POST data.
A bound form allows us to start using built-in validation-related tools: 
first, the is_valid method to check the form's validity, then the cleaned_data attribute
on the form, which contains the values converted from strings to Python objects.

The cleaned_data attribute is only available after the form has been cleaned,
which means the process of "cleaning up" the data and converting it from strings to
Python objects. The cleaning process runs during the is_valid call. You will get
AttributeError raised if you try to access cleaned_data before calling is_valid .

note that unlike when we iterated over all of the POST data, cleaned_data only 
contains form fields. The other data (such as the CSRF token and the submit button 
that was clicked) is present in the POST QueryDict but is not included as 
it does not include form fields.

BUILD-IN FIELD VALIDATION

* required
* max_length
* min_length
* max_value
* min_value
* max_digits
* decimal_places

SUMMARY
--------------------------------------------------

This chapter was an introduction to forms in Django. We introduced some HTML
inputs for entering data onto a web page. We talked about how data is submitted
to a web application and when to use GET and POST requests. We then looked at
how Django's form classes can make generating the form HTML simpler, as well as
allowing the automatic building of forms using models.


7. ADVANCED FORM VALIDATION AND MODEL FORMS
==================================================


