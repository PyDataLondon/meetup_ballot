# coding=utf-8

from unittest import TestCase
from unittest.mock import patch, MagicMock
from meetup_ballot.meetup import MeetupClient

DEFAULT_URL_NAME = "pydatalondon"
DEFAULT_ACCESS_TOKEN = "abcd"


class TestMeetup(TestCase):
    def setUp(self):
        self.client = MeetupClient(access_token=DEFAULT_ACCESS_TOKEN, urlname=DEFAULT_URL_NAME)

    @patch("requests.get")
    def test_send_get_request(self, mocked_get):
        append_url = "rsvps"
        test_params = dict(hello="world")
        self.client.send_get_request(append_url, test_params)

        expected_url = "https://api.meetup.com/{url_name}/{append_url}".format(
            url_name=DEFAULT_URL_NAME, append_url=append_url
        )
        mocked_get.assert_called_with(expected_url, params=test_params, headers=self.client.headers)

    @patch("requests.get")
    def test_get_next_event_id(self, mocked_get):
        fake_id = "123"
        fake_response = [dict(id=fake_id)]
        mocked_get.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value=fake_response)
        )
        actual = self.client.get_next_event_id()

        self.assertEqual(fake_id, actual)

    @patch("requests.get")
    def test_get_member_details(self, mocked_get):
        fake_member_details = dict(name="testbot")
        mocked_get.return_value = MagicMock(
            json=MagicMock(return_value=fake_member_details)
        )
        self.client.get_member_details("abc")

        expected_url = "https://api.meetup.com/2/member/abc"
        expected_params = {"page": 1}

        mocked_get.assert_called_with(url=expected_url, params=expected_params, headers=self.client.headers)

    @patch("requests.get")
    def test_get_member_name(self, mocked_get):
        test_name = "testbot"
        fake_member_details = dict(name=test_name)
        mocked_get.return_value = MagicMock(
            json=MagicMock(return_value=fake_member_details)
        )
        member_name = self.client.get_member_name("abc")
        self.assertEqual(test_name, member_name)

    @patch("requests.get")
    def test_get_next_event_time(self, mocked_get):
        fake_time = "4 December"
        fake_response = [dict(time=fake_time)]
        mocked_get.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value=fake_response)
        )

        next_date = self.client.get_next_event_time()
        self.assertEqual(fake_time, next_date)

    @patch("time.sleep")
    @patch("requests.post")
    def test_mark_rsvps_to_yes(self, mocked_post, _):
        fake_event_id = "event_id"
        fake_member_ids = ["p1", "p2"]
        mocked_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value="OK")
        )
        self.client.mark_rsvps_to_yes(fake_event_id, fake_member_ids)

        expected_url = "https://api.meetup.com/2/rsvp"
        expected_data = {
            "member_id": "p2",
            "event_id": "event_id",
            "rsvp": "yes",
        }
        mocked_post.assert_called_with(expected_url, data=expected_data, headers=self.client.headers)

    @patch("requests.get")
    def test_get_rsvps(self, mocked_get):
        fake_event_id = "event_id"
        mocked_get.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value="OK")
        )
        self.client.get_rsvps(fake_event_id)

        expected_url = (
            "https://api.meetup.com/" + "pydatalondon/events/event_id/rsvps"
        )
        mocked_get.assert_called_with(expected_url, headers=self.client.headers, params=None)

    def test_get_response_wise_rsvps_count(self):
        fake_rsvps = [{"response": "yes"}, {"response": "no"}]
        count = self.client.get_response_wise_rsvps_count(fake_rsvps)

        self.assertEqual({"yes": 1, "no": 1}, count)

    def test_get_coorganizers_and_hosts_from_rsvps(self):
        fake_rsvps = [
            get_rsvp(1, role=True, host=True)
        ]
        response = self.client.get_coorganizers_and_hosts_from_rsvps(
            fake_rsvps
        )
        self.assertEqual([1], response)

    def test_get_member_ids_from_rsvps(self):
        rsvps = [
            get_rsvp(id=1, role=False, host=False),
            get_rsvp(id=2, role=True, host=False),
            get_rsvp(id=3, role=False, host=True),
            get_rsvp(id=4, role=False, host=False),
            get_rsvp(id=5, role=True, host=True),
        ]
        member_ids = self.client.get_member_ids_from_rsvps(rsvps=rsvps)
        self.assertListEqual([1, 4], member_ids)


def get_rsvp(id, role=False, host=False):
    rsvp = {"member": {"id": id, "event_context": {"host": host}}}
    if role:
        rsvp["member"]["role"] = "coorganizer"
    return rsvp
