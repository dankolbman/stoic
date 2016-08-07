Stoic
========
[![Build Status](https://travis-ci.org/dankolbman/stoic.svg?branch=master)](https://travis-ci.org/dankolbman/stoic)
[![Coverage Status](https://coveralls.io/repos/github/dankolbman/stoic/badge.svg)](https://coveralls.io/github/dankolbman/stoic)

A Travel Blahg remake

Installing
----------

Many config options can be set in `.venv` environment exports, and others from
`configs.py`.

#### Database

GPS coords are stored in a postgres database using the PostGIS extension.
This extension will need to be enabled for all databases (Defaults are `stoic`,
`staic_dev`, and `stoic_test`). From the docs:

```SQL
-- Enable PostGIS (includes raster)
CREATE EXTENSION postgis;
-- Enable Topology
CREATE EXTENSION postgis_topology;
```

The database can be initialized with:
```bash
./manage db init
```

Running
-------

Run a local server:
```bash
./manage runserver
```

Run tests
```bash
./manage test
```
