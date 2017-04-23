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

Install cassandra and run:

```bash
$ ./manage dbinit
```

Running
-------

Run a local server:
```bash
$ ./manage runserver
```

Run tests
```bash
$ ./manage test
```
