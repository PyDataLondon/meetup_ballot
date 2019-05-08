from nose.tools import eq_
from unittest.mock import patch, MagicMock
from meetup_ballot import ballot


def test_member_name():
    names = [
        None,
        'Word',
        'A BC',
        'Uncle Bob'
    ]

    actual = [ballot.does_member_name_looks_like_spam(name)
              for name in names]

    expected = [
        True,
        True,
        True,
        False
    ]
    eq_(expected, actual)


@patch('time.sleep')
def test_filter_spam_members(_):
    names = [
        None,
        'Word',
        'A BC',
        'Uncle Bob'
    ]
    mocked_client = MagicMock(
        get_member_name=MagicMock(
            side_effect=names
        )
    )
    actual = ballot.filter_spam_members([1, 2, 3, 4], mocked_client)

    eq_([4], actual)


@patch('meetup_ballot.ballot.filter_spam_members')
@patch('meetup_ballot.ballot.get_environment_variable')
@patch('meetup_ballot.ballot.MeetupClient')
def test_run_ballot(mocked_client_cls, mocked_env, mocked_spam):
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

    actual_attending_number = ballot.run_ballot('access_token', 'url')

    eq_(2, actual_attending_number)


@patch('meetup_ballot.ballot.run_ballot')
@patch('meetup_ballot.ballot.get_environment_variable')
@patch('meetup_ballot.ballot.check_meetup_is_in_less_than_delta_time')
@patch('meetup_ballot.ballot.is_script_ran_from_cron_or_manually_triggered')
def test_main(mocked_script_run_source, mocked_delta_time, mocked_env, mocked_run):
    mocked_script_run_source.return_value = True
    mocked_delta_time.return_value = True
    mocked_env.side_effect = [
        "access_token", "url", "1"
    ]

    ballot.main()
    mocked_run.assert_called_with("access_token", "url")


@patch('meetup_ballot.ballot.get_environment_variable')
def test_is_script_ran_from_cron_or_manually_triggered__one_true(mocked_env):
    mocked_env.side_effect = [True, False]

    script_run = ballot.is_script_ran_from_cron_or_manually_triggered()

    eq_(True, script_run)


@patch('meetup_ballot.ballot.get_environment_variable')
def test_is_script_ran_from_cron_or_manually_triggered__both_false(mocked_env):
    mocked_env.side_effect = [False, False]

    script_run = ballot.is_script_ran_from_cron_or_manually_triggered()

    eq_(False, script_run)
