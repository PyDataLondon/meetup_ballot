from nose.tools import eq_
from unittest.mock import patch, MagicMock
from meetup_ballot import ballot


def test_member_name():
    names = [
        None,
        'Word',
        'A BC',
        'Uncle Bob',
        'ExceptionMemberName'
    ]

    actual = [ballot.does_member_name_looks_like_spam(name)
              for name in names]

    expected = [
        True,
        True,
        True,
        False,
        False
    ]
    eq_(expected, actual)


@patch('time.sleep')
def test_filter_spam_members(_):
    names = [
        None,
        'Word',
        'A BC',
        'Uncle Bob',
        'ExceptionMemberName'
    ]
    mocked_client = MagicMock(
        get_member_name=MagicMock(
            side_effect=names
        )
    )
    actual = ballot.filter_spam_members([1, 2, 3, 4, 5], mocked_client, 'name_exceptions.csv')

    eq_([4, 5], actual)


@patch('meetup_ballot.ballot.filter_spam_members')
@patch('meetup_ballot.ballot.get_environment_variable')
@patch('meetup_ballot.ballot.MeetupClient')
def test_run_ballet(mocked_client_cls, mocked_env, mocked_spam):
    mocked_client_cls.return_value = MagicMock(
        get_response_wise_rsvps_count=MagicMock(
            return_value=dict(yes=100)
        ),
        get_coorganizers_and_hosts_from_rsvps=MagicMock(
            return_value=['co-organizers']
        )
    )

    mocked_env.return_value = 101
    mocked_spam.return_value = ['a', 'b', 'c']

    actual_attending_number = ballot.run_ballot('key', 'url', 'name_exceptions.csv')

    eq_(2, actual_attending_number)


@patch('meetup_ballot.ballot.run_ballot')
@patch('meetup_ballot.ballot.get_environment_variable')
@patch('meetup_ballot.ballot.check_meetup_is_in_less_than_delta_time')
def test_main(mocked_delta_time, mocked_env, mocked_run):
    mocked_delta_time.return_value = True
    mocked_env.side_effect = [
        "key", "url", "1"
    ]

    ballot.main()

    mocked_run.assert_called_with("key", "url")
