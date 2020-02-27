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
- `MEETUP_KEY` (Meetup.com API Access Token)
- `MEETUP_URLNAME` (e.g.: PyData-London-Meetup)
- `MAX_RSVPS` (e.g. 200)
- `RSVP_BEFORE_DAYS` (Number of days before which RSVP should start)
- `TRAVIS_EVENT_TYPE` (If the script is running on travis)
- `MANUAL_BALLOT_TRIGGER` (If the script is manually triggered)

## Getting the Access Token

- Login to https://www.meetup.com/meetup_api/, and create an OAuth Consumer, with redirect_uri as let say https://www.google.com.
- Go to the site: https://secure.meetup.com/oauth2/authorize?client_id=CONSUMER_KEY&response_type=token&redirect_uri=https://www.google.com in your browser (replacing CONSUMER_KEY with your own consumer key).
- Grant it access to your meetup.com account.
- It will redirect you to https://www.google.com, with an access token embedded within the URL. It's not using google.com for anything, it's just needs a site to redirect to.
- Look at the new URL in the search bar, and grab the access_token property.

An access token will usually expire after an hour.

Thanks to https://github.com/simonbrownsb/meetupdata for figuring out the above method.

## Usage Example

```bash
PYTHONPATH='.' python meetup_ballot/ballot.py
```

# Ballot Runner Cron

The ballot runs via Travis' cron which is scheduled for everyday, which checks if the next event is within
environment variable `RSVP_BEFORE_DAYS` days. If that evaluates to True then it runs the ballot.

NOTE: The ballot will run if it runs via Travis cron or build is manually triggered and the `MANUAL_BALLOT_TRIGGER`
environment variable is set to True.

## Testing

* Running Tests

```bash
$ nosetests
```

## Contributing

* Feel free to suggest changes via Pull requests.
