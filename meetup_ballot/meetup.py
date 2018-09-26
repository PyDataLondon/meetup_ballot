# coding=utf-8

import time
import logging
import requests

from collections import Counter

NUM_OF_REQUESTS_TO_SLEEP_AFTER = 2

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
        logging_file = 'meetup.log'
        logging_format = '%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s'
        logging.basicConfig(level=logging.INFO, format=logging_format, filename=logging_file)

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
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]['id']
        else:
            logging.error('No future events scheduled')
            return 0

    def get_member_details(self, member_id):
        """
        Returns member details
        :param member_id: meetup.com id of the member
        :return: json of member details
        """
        url = '{base_url}/2/member/{member_id}'.format(base_url=self.base_url, member_id=member_id)
        response = requests.get(url=url, params={'key': self.key, 'page': 1})
        return response.json()

    def get_member_name(self, member_id):
        """
        Get member name
        :param member_id: meetup.com id of the member
        :return: name of the member.
        """
        member_details = self.get_member_details(member_id)
        return member_details.get('name')

    def get_next_event_time(self):
        """
        Unix Time of next event in milliseconds in UTC.
        :return: int
        """
        response = self.send_get_request({'page': 1}, 'events')
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]['time']
        else:
            logging.info('Next event info response: %s', response.status_code)
            logging.info('Next event info response: %s', response.json())
            logging.error('Either no future events scheduled or unable to fetch any.')
            return float('INF')

    def mark_rsvps_to_yes(self, event_id, member_ids):
        """
        Marks the RSVP of all the members in the member_ids for a given event_id
        :param event_id: id of the event
        :param member_ids: list of member_id
        :return: None
        """
        url = '{base_url}/2/rsvp'.format(base_url=self.base_url)
        total_members = len(member_ids)
        for i in range(total_members):
            if i % NUM_OF_REQUESTS_TO_SLEEP_AFTER == 0:
                time.sleep(1)
            member_id = member_ids[i]
            logging.info('%s/%s Setting RSVP to yes for member_id: %s', i + 1, total_members, member_id)
            data = {'member_id': member_id, 'event_id': event_id, 'rsvp': RSVP_YES, 'key': self.key}
            response = requests.post(url, data=data)
            if response.status_code != 201:
                try:
                    response_json = response.json()
                except Exception:
                    response_json = 'no response json'
                logging.info('Something went wrong! Response code: %s, Response: %s', response.status_code,
                             response_json)
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

    def get_rsvsps_response_wise_count(self, rsvps):
        """
        Get the response wise count of RSVPS.
        :param rsvps:
        :return: Counter dict of response:
        e.g. Counter({'no': 42, 'waitlist': 162, 'yes': 254})
        """
        response = Counter([rsvp['response'] for rsvp in rsvps])
        return response

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
        logging.info('Co-organizers IDs: %s', member_ids)
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
