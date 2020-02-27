# coding=utf-8

from datetime import datetime
from datetime import timedelta
import random
import logging
import os

from meetup_ballot.meetup import MeetupClient

MEETUP_ACCESS_TOKEN_VAR = "MEETUP_KEY"
MEETUP_URLNAME_VAR = "MEETUP_URLNAME"
MAX_RSVPS_VAR = "MAX_RSVPS"
RSVP_BEFORE_DAYS = "RSVP_BEFORE_DAYS"
TRAVIS_EVENT_TYPE = "TRAVIS_EVENT_TYPE"
MANUAL_BALLOT_TRIGGER = "MANUAL_BALLOT_TRIGGER"


def setup_logging():
    """
    Setups logging for the ballot.
    :return: None
    """
    logging_format = (
        "%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO, format=logging_format
    )


def get_environment_variable(var):
    """
    Extracts environment variables
    :param var:
    :return: value of the environment variable.
    """
    try:
        return os.environ[var]
    except KeyError:
        logging.error("Environment variable: %s not found", var)
        raise


def select_random(sample_list, sample_size):
    """
    Select a random sample of size sample_size
    :param sample_list:
    :param sample_size:
    :return:
    """
    sample = random.sample(sample_list, sample_size)
    return sample


def check_meetup_is_in_less_than_delta_time(access_token, meetup_urlname, days):
    """
    Checks if the meetup is less than delta days away. Useful
    for triggering cron.
    :param access_token: Meetup.com API access token
    :param meetup_urlname: Meetup's group API.
    :param days:
    :return: bool True if meetup is less than delta days away else False
    """
    today = datetime.utcnow()
    time_after_delta = today + timedelta(days=days)
    client = MeetupClient(access_token=access_token, urlname=meetup_urlname)
    next_event_time = client.get_next_event_time() / 1000
    return next_event_time < time_after_delta.timestamp()


def check_if_ballot_already_ran(client, rsvps, max_rsvps):
    response = client.get_response_wise_rsvps_count(rsvps)
    logging.info("Response wise RSVPS: %s", response)
    return response["yes"] >= max_rsvps


def does_member_name_looks_like_spam(member_name):
    """Filter bad/spam names"""
    if not member_name:
        return True
    if len(member_name.split()) < 2:
        return True
    for sub_name in member_name.split():
        if len(sub_name) < 2:
            return True
    return False


def filter_spam_members(members):
    """
    Returns a list of good member_ids by filtering the spam members
    :param members: list of member objects
    :return: list of good members
    """
    good_member_ids = []
    for member in members:
        member_id, member_name = member['id'], member['name']
        if not does_member_name_looks_like_spam(member_name):
            logging.info("Good member name: {} (ID: {})".format(member_name, member_id))
            good_member_ids.append(member_id)
        else:
            logging.info("Bad Member name: {} (ID: {})".format(member_name, member_id))
    return good_member_ids


def run_ballot(meetup_acess_token, meetup_urlname):
    """
    Run's the PyData London Meetups's RSVP Ballot.
    :param meetup_acess_token: Meetup.com API access token
    :param meetup_urlname: Url name of the meetup group.
    :return: Attending members count if ballot is run for the
    first time for the given event else 0.
    """

    logging.info("Creating Meetup Client")
    client = MeetupClient(access_token=meetup_acess_token, urlname=meetup_urlname)

    logging.info("Getting next event id")
    next_event_id = client.get_next_event_id()

    logging.info("Next event id: %s", next_event_id)
    event_rsvps = client.get_rsvps(next_event_id)

    logging.info("Next event RSVPS: %s", len(event_rsvps))
    members = client.get_members_from_rsvps(event_rsvps)

    logging.info("Filtering spam members")
    good_member_ids = filter_spam_members(members)

    logging.info("Getting event hosts and coorganizers")
    coorg_hosts_member_ids = client.get_coorganizers_and_hosts_from_rsvps(
        event_rsvps
    )

    response_wise_rsvps = client.get_response_wise_rsvps_count(event_rsvps)
    logging.info("Current RSVP responses: %s", response_wise_rsvps)
    max_rsvps = int(get_environment_variable(MAX_RSVPS_VAR))

    current_rsvps = response_wise_rsvps["yes"]
    rsvps_available = max(max_rsvps - current_rsvps, 0)
    logging.info("RSVPs available %s", rsvps_available)

    rsvps_possible = min(len(good_member_ids), rsvps_available)
    logging.info("RSVPs possible %s", rsvps_possible)

    logging.info("Selecting random: %s members", rsvps_possible)
    random_members = select_random(good_member_ids, rsvps_possible)

    logging.info("Marking RSVPs to Yes for random members")
    attending_members = coorg_hosts_member_ids + random_members
    client.mark_rsvps_to_yes(next_event_id, attending_members)
    return len(attending_members)


def is_script_ran_from_cron_or_manually_triggered():
    try:
        cron_event = get_environment_variable(TRAVIS_EVENT_TYPE)
        manual_trigger = get_environment_variable(MANUAL_BALLOT_TRIGGER)
        return cron_event or manual_trigger
    except KeyError:
        return False


def main():
    """
    Main function which will be executed when this scripted is invoked
    directly. Setups logging, checks if its the right time to run the
    ballot and runs the ballot if its the right time.
    :return: None
    """
    setup_logging()
    meetup_access_token = get_environment_variable(MEETUP_ACCESS_TOKEN_VAR)
    if not is_script_ran_from_cron_or_manually_triggered():
        logging.info('Script is neither ran from cron nor manually triggered')
        return
    meetup_urlname = get_environment_variable(MEETUP_URLNAME_VAR)
    rsvp_before_days = int(get_environment_variable(RSVP_BEFORE_DAYS))
    if check_meetup_is_in_less_than_delta_time(
        meetup_access_token, meetup_urlname, days=rsvp_before_days
    ):
        logging.info(
            "The next meetup is less than %s days ago.", rsvp_before_days
        )
        logging.info("Running the PyData London Meetup's RSVP Ballot")
        try:
            run_ballot(meetup_access_token, meetup_urlname)
        except Exception as e:
            logging.exception(e)
    else:
        logging.info(
            "The next meetup is more than %s days ago.", rsvp_before_days
        )
        logging.info('It"s not the right time to run the ballot.')


if __name__ == "__main__":
    main()
