import requests


def get_event_match_keys_with_vidoes(event_key):
    r = requests.get('http://www.thebluealliance.com/api/v3/event/%s/matches' % event_key, headers={'':''})
    json = r.json()
    match_video = {}
    for match in json:
        if len(match['videos']):
            if match['videos'][0]['type'] == 'youtube':
                match_video[match['key']] = (match['videos'][0]['key'], match['comp_level'])
    return match_video


def get_event_match_outcomes(event_key):
    r = requests.get('http://www.thebluealliance.com/api/v3/event/%s/matches' % event_key,
                     headers={'': ''})
    json = r.json()
    outcomes = {}
    for match in json:
        outcomes[match['key']] = match['winning_alliance']
    return outcomes