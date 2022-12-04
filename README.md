# Digital Archive Server
!! STILL UNDER ACTIVE DEVELOPMENT; RUN AT YOUR OWN RISK !!

This is a Django webserver interface designed to serve content archived with metadata.

The Django Project is stored under the `DigitalArchiveServer` directory.

## Components
### Content Viewer
This Django app holds the interfaces used to serve and sort content to the web. 
It is stored under `DigitalArchiveServer/ContentViewer`.
It is served under `/`.

### Archivers
This django app contains the interfaces used to archive and store new content.
It is stored under `DigitalArchiveServer/Archivers`
It is served under `/archivers/`