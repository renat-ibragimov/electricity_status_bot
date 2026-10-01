from alert_parser import Alert, parse_legacy, parse_new

YELLOW_MSG = ('Одеський район — повітряна тривога, жовтий рівень: '
              'Дронова загроза (жовтий рівень)')
RED_MSG = ('Одеський район — повітряна тривога, червоний рівень: '
           'Ракетна загроза (червоний рівень)')
OFF_MSG = 'Одеський район — відбій повітряної тривоги'


def test_new_yellow():
    assert parse_new(YELLOW_MSG, 'Одеський район') == Alert(
        'yellow', 'Дронова загроза')


def test_new_red():
    assert parse_new(RED_MSG, 'Одеський район') == Alert(
        'red', 'Ракетна загроза')


def test_new_off():
    assert parse_new(OFF_MSG, 'Одеський район') == Alert('off')


def test_new_other_area_ignored():
    assert parse_new(YELLOW_MSG.replace('Одеський', 'Чорноморський'),
                     'Одеський район') is None


def test_new_wording_changes_still_alert():
    assert parse_new('Одеський район — тривога, рівень жовтий',
                     'Одеський район') == Alert('yellow')
    assert parse_new('Одеський район — повітряна тривога, червоного рівня',
                     'Одеський район') == Alert('red')
    assert parse_new('Одеський район — повітряна тривога, помаранчевий '
                     'рівень: Нова загроза (помаранчевий рівень)',
                     'Одеський район') == Alert('on', 'Нова загроза')


def test_news_are_not_alerts():
    area = 'Одеський район'
    news = [
        'Під час повітряної тривоги в Одесі пошкоджено будівлю. '
        'Одеський район — червоний рівень небезпеки не оголошувався.',
        'Одеський район: ' + 'повітряна тривога, жовтий рівень. ' * 20,
        'Червоний Хрест передав допомогу. Відбій тривоги був о 07:56.',
        'Одеса — повітряна тривога, жовтий рівень: Дронова загроза',
        '🟡 Одеський район — повітряна тривога, жовтий рівень: Дронова '
        'загроза (жовтий рівень)',
    ]
    assert [parse_new(t, area) for t in news[:4]] == [None] * 4
    assert parse_new(news[4], area) == Alert('yellow', 'Дронова загроза')


def test_new_no_area_filter():
    assert parse_new(RED_MSG) == Alert('red', 'Ракетна загроза')


def test_new_unrelated_message():
    assert parse_new('Доброго ранку! 1 жовтня 2026 р.') is None
    assert parse_new('') is None


def test_legacy():
    assert parse_legacy('Одесса тревога!', 'тревога!',
                        'тревоги') == Alert('on')
    assert parse_legacy('Одесса отбой тревоги', 'тревога!',
                        'тревоги') == Alert('off')
    assert parse_legacy('Доброе утро', 'тревога!', 'тревоги') is None
