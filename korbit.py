import json
import requests
import time

try:
    import config
except:
    raise Exception('Could not import config.py')


BASE_URL = 'https://api.korbit.co.kr/v1'


def load_dict(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def store_dict(filename, dic):
    with open(filename, 'w') as f:
        f.write(json.dumps(dic))


def get(url_suffix, **params):
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.get(url, params=params)

    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception(str(res))


def post(url_suffix, **post_data):
    url = '{}/{}'.format(BASE_URL, url_suffix)

    res = requests.post(url, data=post_data)

    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception(str(res))


def access_token():
    token_dict = None

    try:
        # FIXME: This will cause an issue when the store token is expired
        token_dict = load_dict('token.json')
    except:
        token_dict = post('oauth2/access_token',
                          client_id=config.API_KEY,
                          client_secret=config.API_SECRET,
                          username=config.USERNAME,
                          password=config.PASSWORD,
                          grant_type='password')

    store_dict('token.json', token_dict)

    return token_dict


def nonce():
    return long(time.time() * 1000)


def constants():
    return get('constants')


def detailed_ticker():
    return get('ticker/detailed')


def wallet():
    token = access_token()
    return get('user/wallet', access_token=token['access_token'],
               nonce=nonce() + 800)


if __name__ == '__main__':
    print wallet()
