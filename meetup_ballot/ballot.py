# coding=utf-8

import random
import logging
import os

from meetup_ballot.meetup import MeetupClient

MEETUP_KEY_VAR = 'MEETUP_KEY'
MEETUP_URLNAME_VAR = 'MEETUP_URLNAME'
MAX_RSVPS_VAR = 'MAX_RSVPS'


def setup_logging():
    logging_format = '%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=logging_format)


def get_environment_variable(var):
    try:
        return os.environ[var]
    except KeyError as excep:
        logging.error('Environment variable: %s not found', var)
        raise excep


def select_random(sample_list, sample_size):
    sample = random.sample(sample_list, sample_size)
    return sample


def run_ballot():
    meetup_key = get_environment_variable(MEETUP_KEY_VAR)
    meetup_urlname = get_environment_variable(MEETUP_URLNAME_VAR)

    logging.info('Creating Meetup Client')
    client = MeetupClient(key=meetup_key, urlname=meetup_urlname)

    logging.info('Getting next event id')
    next_event_id = client.get_next_event_id()

    logging.info('Next event id: %s', next_event_id)
    event_rsvps = client.get_rsvps(next_event_id)

    logging.info('Next event RSVPS: %s', len(event_rsvps))
    member_ids = client.get_member_ids_from_rsvps(event_rsvps)
    max_rsvps = int(get_environment_variable(MAX_RSVPS_VAR))

    logging.info('Get event hosts and coorganizers')
    coorg_hosts_member_ids = client.get_coorganizers_and_hosts_from_rsvps(event_rsvps)

    logging.info('Selecting random: %s members', max_rsvps)
    random_members = select_random(member_ids, max_rsvps)

    logging.info('Marking RSVPs to Yes for random members')
    attending_members = coorg_hosts_member_ids + random_members
    client.mark_rsvps_to_yes(next_event_id, attending_members)


if __name__ == '__main__':
    setup_logging()
    run_ballot()
