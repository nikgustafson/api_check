
# ARGUS PANOPTES - api check suite for OrderCloud

## How to Run

>> pytest panoptes 

if you wish to run it against production:

>> pytest panoptes --ENV=prod

## Documentation

Different suites:

`pytest panoptes -m smoke`

Smoke Tests are for before and after a deploy, to verify that the deploy *actually* deployed what you wanted it to.

Smoke Tests verify:
- that the API ENV is responding
- that API authentication works (both buyer and seller)
- that the database can be accessed (via API object creation, retrieval, delete & verification)
- DevCenter website is responding
- --DevCenter authentication works and redirects correctly--

`pytest panoptes -m search`


## Docker Build & Run

to build dockerfile:
    from containing `api-check` folder:
    `docker build -t panoptes panoptes`
to run dockerfile:
    `docker run panoptes`


## TODO:

- [ ] switch all request calls to try/catch
- [ ] add sphinx documentation

- [ ] add non established buyer user runs to tests -- ex, anon, etc


