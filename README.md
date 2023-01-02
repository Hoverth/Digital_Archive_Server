# Digital Archive Server
### !! STILL UNDER ACTIVE DEVELOPMENT; STABILITY IS NOT ASSURED !!

This is a webserver designed to serve archived internet-based content (such as websites, webpages, or file collections) with metadata.

This project makes use of Django, PostgreSQL, RabbitMQ, Celery and nginx inside Docker containers.

Presently, this project consists only of a Django backend, with a basic HTML frontend. 
This may change to include a backend API and a JavaScript frontend, but there are no plans archivedfor this to happen in the foreseeable future.

The Django project is stored under the `DigitalArchiveServer` directory.

## Requirements
Both `docker` and `docker-compose` are required to run this project

## Running & Installation
Firstly, `git clone` or otherwise download this repository onto the target system.

Check and follow the instructions in `.env` and `.env.db`. This makes sure that your instance is secure, and able to be accessed.

NOTE: This assumes there is not an already set up web server on the server this is being installed on. If there is, it will conflict with the nginx reverse proxy that is built-in.
To fix, in `docker-compose.yml` change `80` in `"1337:80"` under ports to whatever outwards-facing port you want.

NOTE: The static directory setup in `docker-compose.yml` (the default is `/srv/digital-archive-server/`) needs to be writable `sudo chmod 777 /srv/digital-archive-server/`.

Then `sudo docker-compose up -d --build` to build and start the container.

Use `sudo docker-compose exec web python DigitalArchiveServer/manage.py createsuperuser` to create a starter super-user

Now your instance should be up and running, and accessible from your server's IP address.

## Components
### Content Viewer
This Django app holds the interfaces used to serve and sort content to the web. 
It is stored under `DigitalArchiveServer/ContentViewer`.
It is served under `/`.

#### Views
 - `/` - A customizable view that points to any other view as the server's index page
 - `/content` - A ListView that shows all content archived by the server, sorted by the time retrieved
 - `/content/[content-id]` - A DetailView that shows the details of the content
 - `/tags` - A ListView that shows all the tags that the server has indexed, sorted by number of references
 - `/tags/0` - A ListView that lists the content without any set tags
 - `/tag/[tag-id]` - A ListView that shows the details of a tag and lists the content with that tag
 - `/creators` - A ListView that shows all the creators of the content stored by the server, sorted alphabetically
 - `/creator/0` - A ListView that lists the content without a set creator
 - `/creator/[creator-id]` - A ListView that shows the details of a creator and lists the content created by that creator
 - `/search` - A ListView that shows content that matches the relevant submitted query

### Archivers
This directory contains the interfaces used to archive and store new content from the web.
It is stored under `DigitalArchiveServer/ContentManager/Archivers`
It is served under `/archivers`

#### ArchiveWorkers
The archive is populated using content obtained by ArchiveWorkers. These are individual python plugins that extend the base `ArchiveWorker` class. 
These ArchiveWorkers contain their own web interface, with a base interface provided by the parent class, and pass an action off to the celery worker for asynchronous processing.

By default, this project comes with a single archive worker (GenericArchiveWorker), used for generic web archiving. Currently it can archive single files and complete webpages.

#### Views
 - `/archivers` - A list of all available ArchiveWorkers
 - `/archivers/[archiver-codename]` - A view on that ArchiveWorker, allowing you to see the logs and request archival

### Users & Groups
A basic user can only see non-adult content, with no benefits over non-logged-in users. Users mostly exist to be assigned to groups, and to track seen and liked content

There are two groups you can assign to users, Adult and Archivers.

#### Views 
 - `/user/[username]` - A page showing details about a user
 - `/user/[username]/seen` - A ListView showing the content seen by a user 
 - `/user/[username]/liked` - A ListView showing the content liked by a user
 - `/user/[username]/collections` - A ListView showing the collections owned by a user

#### Groups
##### Adult
Assigning a user to this group means that they can access anything marked as adult content

##### Archivers
Archivers can access the archivers page and can execute orders to ArchiveWorkers to start archiving things
