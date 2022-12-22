# Digital Archive Server
!! STILL UNDER ACTIVE DEVELOPMENT; RUN AT YOUR OWN RISK !!

This is a Django webserver interface designed to serve content archived with metadata.

The Django Project is stored under the `DigitalArchiveServer` directory.

## Running with docker
`sudo docker-compose up -d --build` to build and start the container
NOTE: the static directory setup in `docker-compose.yml` (the default is `/srv/digital-archive-server/`) needs to be writable `sudo chmod 777 /srv/digital-archive-server/`
`sudo docker-compose exec web python DigitalArchiveServer/manage.py createsuperuser` to create a super-user

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

### Archivers
This directory contains the interfaces used to archive and store new content.
It is stored under `DigitalArchiveServer/ContentManager/Archivers`
It is served under `/archivers`

#### Views
 - `/archivers` - A list of all available archivers
 - `/archivers/[archiver-codename]` - A DetailView on that archiver, allowing you to see the logs and request archival

### Users
There are two groups you can assign to users, Adult and Archivers.

#### Adult
Assigning a user to this group means that they can access anything marked as adult content

#### Archivers
Archivers can access the archivers page and can start archive workers archiving things
