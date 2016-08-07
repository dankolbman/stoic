Traveled
========

A Travel Blahg remake

Installing
----------

Many config options can be set in `.venv` environment exports, and others from
`configs.py`.

#### Database

GPS coords are stored in a postgres database using the PostGIS extension.
This extension will need to be enabled for all databases (Defaults are `traveled`,
`traveled_dev`, and `traveled`). From the docs:

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
