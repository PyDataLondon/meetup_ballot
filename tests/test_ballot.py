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
