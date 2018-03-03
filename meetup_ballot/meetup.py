# coding=utf-8

import logging
import requests

RSVP_YES = 'yes'


class MeetupClient:
    """
    Client for accessing Meetup.com API
    """

    def __init__(self, key, urlname=None):
        self.key = key
        self.urlname = urlname
        self.base_url = 'https://api.meetup.com'
        self.url = '{}/{}'.format(self.base_url, self.urlname)
        self.setup_logging()

    def setup_logging(self):
        """
        Setups the logging.
        :return: None
        """
        logging_format = '%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s'
        logging.basicConfig(level=logging.INFO, format=logging_format)

    def send_get_request(self, params, append_url):
        """
        Send GET request to meetup's API.
        :param params: dict of params
        :param append_url: string to append in the url.
        :return: response of the GET request.
        """
        url = '{default_url}/{append_url}'.format(default_url=self.url, append_url=append_url)
        default_params = {'key': self.key}
        req_params = {**params, **default_params}
        response = requests.get(url, params=req_params)
        return response

    def get_next_event_id(self):
        """
        Id of the next meetup of the group.
        :return:
        """
        response = self.send_get_request({'page': 1}, 'events')
        return response.json()[0]['id']

    def get_next_event_time(self):
        """
        Unix Time of next event in milliseconds in UTC.
        :return: int
        """
        response = self.send_get_request({'page': 1}, 'events')
        return response.json()[0]['time']

    def mark_rsvps_to_yes(self, event_id, member_ids):
        """
        Marks the RSVP of all the members in the member_ids for a given event_id
        :param event_id: id of the event
        :param member_ids: list of member_id
        :return: None
        """
        url = '{base_url}/2/rsvp'.format(base_url=self.base_url)
        for member_id in member_ids:
            logging.info('Setting RSVP to yes for member_id: %s', member_id)
            data = {'member_id': member_id, 'event_id': event_id, 'rsvp': RSVP_YES, 'key': self.key}
            response = requests.post(url, data=data)
            if response.status_code != 201:
                logging.info('Something went wrong! Response code: %s', response.status_code)
            else:
                logging.info('Marked member_id: %s"s RSVP as Yes', member_id)

    def get_rsvps(self, event_id):
        """
        Get all the RSVPS for a given event id.
        :param event_id:
        :return: json response
        """
        append_url = 'events/{event_id}/rsvps'.format(event_id=event_id)
        response = self.send_get_request({}, append_url=append_url)
        return response.json()

    def get_coorganizers_and_hosts_from_rsvps(self, rsvps):
        """
        Get the RSVPS of all the coorganizers of the meetup group.
        :param rsvps:
        :return: list of member ids.
        """
        member_ids = []
        for rsvp in rsvps:
            member = rsvp['member']
            if member.get('role') or member['event_context']['host']:
                member_ids.append(rsvp['member']['id'])
        return member_ids

    def get_member_ids_from_rsvps(self, rsvps):
        """
        Get member_ids of non-coorganizers and non-hosts from the RSVPS.
        :param rsvps:
        :return: list of member ids.
        """
        member_ids = []
        for rsvp in rsvps:
            member = rsvp['member']
            if not member.get('role') and not member['event_context']['host']:
                member_ids.append(rsvp['member']['id'])
        return member_ids
