# coding=utf-8

import unittest
from meetup_ballot.meetup import MeetupClient


class TestMeetup(unittest.TestCase):

    @staticmethod
    def get_rsvp(id, role=False, host=False):
        rsvp = {
            'member': {
                'id': id,
                'event_context': {'host': host}
            },
        }
        if role:
            rsvp['member']['role'] = 'coorganizer'
        return rsvp

    def test_get_member_ids_from_rsvps(self):
        rsvps = [
            self.get_rsvp(id=1, role=False, host=False),
            self.get_rsvp(id=2, role=True, host=False),
            self.get_rsvp(id=3, role=False, host=True),
            self.get_rsvp(id=4, role=False, host=False),
            self.get_rsvp(id=5, role=True, host=True)
        ]
        client = MeetupClient(key='abcd')
        member_ids = client.get_member_ids_from_rsvps(rsvps=rsvps)
        self.assertListEqual([1, 4], member_ids)
