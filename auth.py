import time
import requests
from main_config import ya_login, ya_password, my_user_agent
from pyquery import PyQuery
from pickle import dump


def auth():
    try:
        session = requests.Session()
        r_welcome = session.get(
            'https://passport.yandex.ru/auth/welcome?origin=lyceum&retpath=https%3A%2F%2Flyceum.yandex.ru%2F',
            headers={'User-Agent': my_user_agent})
        pyquery_object = PyQuery(r_welcome.text)
        csrf_token = pyquery_object('input[name=csrf_token]').val()
        process_uuid_href = pyquery_object('.Button2_type_link:first').attr('href')
        process_uuid = process_uuid_href[process_uuid_href.find('process_uuid=') + 13:]
    except Exception as e:
        return f'Exit script. Error at start session: {e}'

    time.sleep(2)

    try:
        r_start = session.post('https://passport.yandex.ru/registration-validations/auth/multi_step/start',
                               {'csrf_token': csrf_token, 'login': ya_login, 'process_uuid': process_uuid},
                               headers={'User-Agent': my_user_agent, 'Referer': 'https://passport.yandex.ru/',
                                        'X-Requested-With': 'XMLHttpRequest'})
        track_id = r_start.json()['track_id']
    except Exception as e:
        return f'Exit script. Error at multi_step/start: {e}'

    time.sleep(2)

    try:
        r_password = session.post('https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
                                  {'csrf_token': csrf_token, 'track_id': track_id, 'password': ya_password,
                                   'retpath': 'https://lyceum.yandex.ru/'},
                                  headers={'User-Agent': my_user_agent,
                                           'Referer': 'https://passport.yandex.ru/',
                                           'X-Requested-With': 'XMLHttpRequest'})
        phone_id = session.post('https://passport.yandex.ru/registration-validations/auth/challenge/submit',
                                {'csrf_token': csrf_token, 'track_id': track_id}, headers={'User-Agent': my_user_agent,
                                                                                           'Referer': 'https://passport.yandex.ru/',
                                                                                           'X-Requested-With': 'XMLHttpRequest'}).json()[
            'challenge']['phoneId']
    except Exception as e:
        return f'Exit script. Error at multi_step/commit_password: {e}'

    time.sleep(2)

    try:
        r_submit_to_code = session.post('https://passport.yandex.ru/registration-validations/phone-confirm-code-submit',
                                        {'track_id': track_id,
                                         'csrf_token': csrf_token, 'phone_id': phone_id, 'confirm_method': 'by_sms',
                                         'isCodeWithFormat': True},
                                        headers={'User-Agent': my_user_agent,
                                                 'Referer': 'https://passport.yandex.ru/',
                                                 'X-Requested-With': 'XMLHttpRequest'})
        r_confirm_code = session.post('https://passport.yandex.ru/registration-validations/phone-confirm-code',
                                      {'track_id': track_id,
                                       'csrf_token': csrf_token, 'code': int(input('Введите код из СМС:  '))},
                                      headers={'User-Agent': my_user_agent,
                                               'Referer': 'https://passport.yandex.ru/',
                                               'X-Requested-With': 'XMLHttpRequest'})
        r_submit = session.post('https://passport.yandex.ru/registration-validations/auth/challenge/commit',
                                {'track_id': track_id,
                                 'csrf_token': csrf_token, 'challenge': 'phone_confirmation'},
                                headers={'User-Agent': my_user_agent,
                                         'Referer': 'https://passport.yandex.ru/',
                                         'X-Requested-With': 'XMLHttpRequest'})
    except Exception as e:
        return f'Exit script. Error at registration-validations/phone-confirm-code: {e}'

    time.sleep(3)

    check = session.get('https://lyceum.yandex.ru/', headers={'User-Agent': my_user_agent}).text
    try:
        pyquery_object = PyQuery(check)
        name = pyquery_object('span.user-account__name:first').text()
        if name:
            file = open('auth.pkl', 'wb')
            dump(session, file)
            file.close()
            return 'Everything OK!'
    except Exception as e:
        return f'Exit script. Error at check auth: {e}'


if __name__ == '__main__':
    auth()
