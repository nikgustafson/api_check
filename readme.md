
# ARGUS PANOPTES - api check suite for OrderCloud



## How to Run Locally

>> pytest panoptes 

if you wish to run it against production:

>> pytest panoptes --ENV=prod

## Docker Build & Run

to build dockerfile:
    from containing `api-check` folder:
    `docker build -t panoptes panoptes`
to run dockerfile:
    `docker run panoptes`

The dockerfile uses the `panoptes/runScript.py` to run several test sub-suites, mostly using the pytest [mark]() syntax. These tests are run against both QA and Prod, and results can be analyzed using [Tesults](https://www.tesults.com/results)

## Test Suites


### `pytest panoptes -m smoke`

Smoke Tests are for before and after a deploy, to verify that the deploy *actually* deployed what you wanted it to.

Smoke Tests verify:
- that the API ENV is responding
- that API authentication works (both buyer and seller)
- that the database can be accessed (via API object creation, retrieval, delete & verification)
- DevCenter website is responding
- basic message senders are correctly triggering and emails are recieved for them (emails are through [mailinator]())
- --DevCenter authentication works and redirects correctly--

### `pytest panoptes -m search`

These tests cover the new search 2.0 material, such as faceted navigation and elastic search queries

### `pytest panoptes -m load`

These are the "poor man's load tests", where a lot of common calls are run against the api. Unlike the full Locust load tests, they do not run full end to end tests, and they are focused on testing performance-sensitive queries such as /me/products.


## TODO:

### Upkeep
- [ ] switch *all* request calls to try/catch
- [ ] add sphinx documentation

### Expand Coverage
- [ ] add non established buyer user runs to tests -- ex, anon, etc
- [ ] repair and improve xp with depths


