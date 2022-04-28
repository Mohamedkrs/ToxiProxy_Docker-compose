from random import uniform
import time

from toxiproxy import Toxiproxy
import json
import os
import re


def create_proxy(config, proxy):
    proxy = proxy.populate(config)
    return proxy


def wait(duration):
    smms = re.sub("\d", "", duration)
    duration = int(re.sub("\D", "", duration))
    match smms:
        case 'ms':
            return duration/1000
        case 's':
            return duration
        case 'm':
            return duration*60


def activate_toxics(toxic, proxy, duration, duration_offset=0, enable=True):
    duration=duration-uniform(-duration_offset, duration_offset)
    for tox in toxic['toxics']:
        if tox['type'] == 'down':
            if enable:
                proxy[tox['proxy']].disable()
                print('disabling {} proxy for {}s'.format(
                    proxy[tox['proxy']].name, duration))
            else:
                proxy[tox['proxy']].enable()
                print('Enabling {} proxy. Waiting {}s for next injection.'.format(
                    proxy[tox['proxy']].name, duration))
        else:
            if enable:
                proxy[tox['proxy']].add_toxic(
                    type=tox['type'], attributes=tox['attributes'], name=tox['name'])
                print('injecting {} toxic to {} for {}s'.format(
                    tox['name'], proxy[tox['proxy']].name, duration))

            else:
                proxy[tox['proxy']].destroy_toxic(tox['name'])
                print('resetting {} toxic in {}. Waiting {}s for next injection.'.format(
                    tox['name'], proxy[tox['proxy']].name, duration))
    time.sleep(duration)


def inject_toxins(toxic, proxy):
    repetition = toxic['times']
    pause = wait(toxic['pause'])
    pause_offset = wait(toxic['pause_offset'])
    duration = wait(toxic['duration'])
    duration_offset = wait(toxic['duration_offset'])
    if repetition == 0:
        for tox in toxic['toxics']:
            try:
                proxy[tox['proxy']].add_toxic(
                    type=tox['type'], attributes=tox['attributes'], name=tox['name'])
                print('injecting {} toxic to {}'.format(
                    tox['name'], proxy[tox['proxy']].name))
            except Exception as e:
                print('can\'t inject {} toxic to {}: {}'.format(
                    tox['name'], proxy[tox['proxy']].name, repr(e.args)))
    else:
        for rep in range(repetition):
            activate_toxics(toxic, proxy, duration, duration_offset)
            activate_toxics(toxic, proxy, pause, pause_offset, False)
            print( 'Number of repetitions left is {}'.format(repetition-rep-1))


def __main__():
    toxiproxy = Toxiproxy()
    with open('./config/Config.json', 'r') as f:
        data = json.load(f)
    proxies = data['configuration']
    toxics = data['Toxics']

    toxiproxy.update_api_consumer("toxiproxy", 8474)

    toxiproxy.destroy_all()
    proxy = create_proxy(proxies, toxiproxy)
    print('Waiting for {} before getting evil'.format(data['waitBeforeInjectingToxics']))
    time.sleep(wait(data['waitBeforeInjectingToxics']))
    for toxic in toxics:
        inject_toxins(toxic, proxy)


if __name__ == '__main__':
    __main__()
