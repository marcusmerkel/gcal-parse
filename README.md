# gcal-parse

## A Google Calendar html parser with Python

*Made by Marcus Merkel for CS50's Final Project*

**gcal-parse is a webtool that calls the Google Calendar API to parse a list of events in html. I was in need of something like this for my own webpage - so I made it :-)**

Upon opening /, you will be asked to provide a Google Calendar ID, the maximum number of events you want to retrieve and optionally a Performer (in case all the events are being performed by one artist - like in my case [useful for the invisible meta tags]) and a list of Categories.

The application will then make an API Call to Google's Calendar API with a Service Acccount I obtained earlier. Every unknown API access will imply an authorization process on Google's side. To incorporate this into this web application, I would have to get an own server, register an authorized domain with Google, and much more - so I decided to *stay on localhost with this for now*.

The app will gather a list of events and display them in a certain way:
* First the app will try to distinguish the Location Name from the Location Address and will fill these in a location-meta-tag for each event
* In case you provided an artist's name via "Performer", the meta tag for this will be written in every single event
* In case you provided a list of event categories, the app will search the description texts for these keywords and - if successful - display the event category

This data is being displayed on the next page with a responsive layout (made with Bootstrap 4.4). I also took a shot at responsive font resizing. You are being shown a list of events, with Day and Month on the left, details in the middle, and a "More" button on the right. - If there is no description and no location data, the "More" button is omitted. - By clicking on the more button, the view expands to show the event description (which corresponds to the "Notes" in Google Calendar), the Location Name and Location Address. In the bottom right corner, there is a link sending you to an automatic query in Google Maps, looking for that location. Clicking the button will close the detailed view again.

--------
In this project, I learned a lot(!) about how to deal with responsive layout and flexbox, and I explored jQuery. Also I went a lot deeper into Jinja - and now I'm very excited what's next. Looking forward to CS50 Web Development!

This was CS50. :-)