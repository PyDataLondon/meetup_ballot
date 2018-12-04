# Pydata London Meetup Ballot

[![Build Status](https://travis-ci.org/PyDataLondon/meetup_ballot.svg?branch=master)](https://travis-ci.org/PyDataLondon/meetup_ballot) [![Coverage](https://codecov.io/gh/PyDataLondon/meetup_ballot/branch/master/graph/badge.svg)](https://codecov.io/gh/PyDataLondon/meetup_ballot/branch/master)



> Used to select members for the next meetup. 

## Installation

* Create a virtualenv
* Install Requirements

```bash
$ pip install -r requirements.txt
```

* Following environment variables needs to be set:
  - `MEETUP_KEY` (Meetup.com API Key)
  - `MEETUP_URLNAME` (e.g.: PyData-London-Meetup)
  - `MAX_RSVPS` (e.g.: 200)

## Usage Example

```bash
PYTHONPATH='.' python meetup_ballot/ballot.py
```

## Testing

* Running Tests

```bash
$ python -m unittest discover tests
```

## Contributing

* Feel free to suggest changes via Pull requests.
