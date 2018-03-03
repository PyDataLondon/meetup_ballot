# coding=utf-8

import os

from meetup import MeetupClient

MEETUP_KEY_VAR = 'MEETUP_KEY'
MEETUP_URLNAME_VAR = 'MEETUP_URLNAME'


def get_environment_variable(var):
    return os.environ[var]


def run_ballot():
    meetup_key = get_environment_variable(MEETUP_KEY_VAR)
    meetup_urlname = get_environment_variable(MEETUP_URLNAME_VAR)
    client = MeetupClient(key=meetup_key, meetup_urlname=meetup_urlname)
    next_event_id = client.get_next_event_id()
    event_rsvps = client.get_rsvps(next_event_id)
    member_ids = client.get_member_ids_from_rsvps(event_rsvps)
    client.mark_rsvps_to_yes(member_ids)


if __name__ == '__main__':
    run_ballot()
