#!/usr/bin/env python
import json
import getpass

class Config:
    email_address  = None
    server_address = None
    password       = None

    def __init__(self, data):
        self._validate(data)
        self.email_address = data['email_address']
        self.server_address = data['server_address']

        self.password = data['password'] if 'password' in data else getpass.getpass()

    def _validate(self, data):
        if 'email_address' not in data:
            raise ValueError('email_address is missing from config')

        if 'server_address' not in data:
            raise ValueError('server_address is missing from config')


def load():
    with open('config.json') as json_data:
        return Config(json.load(json_data))

if __name__ == '__main__':
    config = load()
    print('Email Address  :', config.email_address)
    print('Server Address :', config.server_address)
    print('Password       :', config.password)
