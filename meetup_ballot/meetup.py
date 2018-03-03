# coding=utf-8

import logging
import requests

RSVP_YES = 'yes'


class MeetupClient:

    def __init__(self, key, urlname=None):
        self.key = key
        self.urlname = urlname
        self.base_url = 'https://api.meetup.com'
        self.url = '{}/{}'.format(self.base_url, self.urlname)
        self.setup_logging()

    def setup_logging(self):
        logging_format = '%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s'
        logging.basicConfig(level=logging.INFO, format=logging_format)

    def send_get_request(self, params, append_url):
        url = '{default_url}/{append_url}'.format(default_url=self.url, append_url=append_url)
        default_params = {'key': self.key}
        req_params = {**params, **default_params}
        response = requests.get(url, params=req_params)
        return response

    def get_next_event_id(self):
        response = self.send_get_request({'page': 1}, 'events')
        return response.json()[0]['id']

    def mark_rsvps_to_yes(self, event_id, member_ids):
        url = '{base_url}/2/rsvp'.format(base_url=self.base_url)
        for member_id in member_ids:
            logging.info('Setting RSVP to yes for member_id: %s', member_id)
            data = {'member_id': member_id, 'event_id': event_id, 'rsvp': RSVP_YES, 'key': self.key}
            response = requests.post(url, data=data)
            if response.status_code != 201:
                logging.info('Something went wrong! Response code: %s', response.status_code)
            else:
                logging.info('Marked member_id: {}"s RSVP as Yes')


    def get_rsvps(self, event_id):
        append_url = 'events/{event_id}/rsvps'.format(event_id=event_id)
        response = self.send_get_request({}, append_url=append_url)
        return response.json()

    def get_member_ids_from_rsvps(self, rsvps):
        member_ids = []
        for rsvp in rsvps:
            member = rsvp['member']
            if not member.get('role') and not member['event_context']['host']:
                member_ids.append(rsvp['member']['id'])
        return member_ids
