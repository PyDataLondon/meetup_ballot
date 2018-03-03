echo "Exporting environment variables"
export $(cat .env | xargs)
echo "Starting Ballot Runner"
PYTHONPATH='.' python meetup_ballot/ballot.py
echo "Execution complete! Check logs in ballot.log & meetup.log"
