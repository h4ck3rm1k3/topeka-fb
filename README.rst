Facebook/Heroku Lawrence App -- Python
====================================

Lawrence Kansas app for all things Lawrence. 

(but you will be able to use this for any location)


Testing facebook
====================================
An important part of this app is the offline testing mode, it allows you to test without facebook.
in the cache/ directory you place json files. If there is a .private file it will be loaded first.

The program facebookserver.py implements the limited api that the program facebookgeoapp.py calls into. 


Ideas for the app :
====================================


Openstreetmap map of the city

Integration with facebook pages, show pages in the area that you have not discovered yet.
Show upcoming events in the area on the map
   Take the address/location from fb and check if it is in a radius from the osm location

Integration with foursquare : show people and places in the area.

Google plus :google places integration.

Twitter :twitter integration.

Website scraping :

   updating osm with links found 
   extracting addresses from websites

Wikipedia :
   show wikipedia articles

Phototagging :
   show commons photos
   allow hosting of photos on archive.com
   allow hosting of photos on commons.com
   allow transfer of FB photos to commons.com
   allow geotagging of photos
   
Modules :
   Leaflet : be able to pull a list of locations via api and display on the leaflet, open layers as well
   Cache : be able to cache all the data so that you can test offline.
   Local : be able to run the thing without facebook at all. What about diaspora or any other thing like wordpress/drupal?

OSM : 
   Be able to use the OSM api directly from facebook, be able to register on OSM using oauth and then share the data you own on osm.   


Run locally
-----------

Set up a Virtualenv and install dependencies::

    virtualenv --no-site-packages env/
    source env/bin/activate
    pip install -r requirements.txt

`Create an app on Facebook`_ and set the Website URL to
``http://localhost:5000/``.

Copy the App ID and Secret from the Facebook app settings page into
your ``.env``::

    echo FACEBOOK_APP_ID=12345 >> .env
    echo FACEBOOK_SECRET=abcde >> .env

Launch the app with Foreman_::

    foreman start

.. _Create an app on Facebook: https://developers.facebook.com/apps
.. _Foreman: http://blog.daviddollar.org/2011/05/06/introducing-foreman.html

Deploy to Heroku via Facebook integration
-----------------------------------------

The easiest way to deploy is to create an app on Facebook and click
Cloud Services -> Get Started, then choose Python from the dropdown.
You can then ``git clone`` the resulting app from Heroku.

Deploy to Heroku directly
-------------------------

If you prefer to deploy yourself, push this code to a new Heroku app
on the Cedar stack, then copy the App ID and Secret into your config
vars::

    heroku create --stack cedar
    git push heroku master
    heroku config:add FACEBOOK_APP_ID=12345 FACEBOOK_SECRET=abcde

Enter the URL for your Heroku app into the Website URL section of the
Facebook app settings page, hen you can visit your app on the web.
