#!/usr/bin/env bash
echo "Exporting environment variables from .env"
export $(cat .env | xargs)
echo "Starting Ballot Runner"
PYTHONPATH='.' python3 meetup_ballot/ballot.py
echo "Execution complete! Check logs in ballot.log & meetup.log"
