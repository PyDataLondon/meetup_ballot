# coding=utf-8

import requests


class MeetupClient:

    def __init__(self, key, meetup_urlname=None):
        self.key = key
        self.meetup_urlname = meetup_urlname
        self.base_url = 'https://api.meetup.com'
        self.url = '{}/{}'.format(self.base_url, self.meetup_urlname)

    def send_request(self, params, append_url):
        url = '{default_url}/{append_url}'.format(default_url=self.url, append_url=append_url)
        default_params = {'key': self.key}
        req_params = {**params, **default_params}
        response = requests.get(url, params=req_params)
        return response

    def get_next_event_id(self):
        response = self.send_request({'page': 1}, 'events')
        return response.json()[0]['id']

    def mark_rsvps_to_yes(self, member_ids):
        pass

    def get_rsvps(self, event_id):
        append_url = 'events/{event_id}/rsvps'.format(event_id=event_id)
        response = self.send_request({}, append_url=append_url)
        return response.json()

    def get_member_ids_from_rsvps(self, rsvps):
        member_ids = []
        for rsvp in rsvps:
            member = rsvp['member']
            if not member.get('role') and not member['event_context']['host']:
                member_ids.append(rsvp['member']['id'])
        return member_ids
