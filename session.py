# -*- coding:utf-8 -*-

import uuid
import hashlib
import hmac

import ujson
import redis

class SessionData(dict):
    def __init__(self, session_id, hmac_key):
        self.session_id, self.hmac_key = session_id, hmac_key


class Session(SessionData):
    def __init__(self, session_manager, request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler
        # try to get current session if exist
        pass


class SessionManager(object):
    def __init__(self, secret, store_options, session_timeout):
        self.secret, self.store_options = secret, store_options
        self.redis = redis.StrictRedis(host=store_options.get('redis_host')
        , port=store_options.get('redis_port')
        , password=store_options.get('redis_pwd'))

    def _fetch(self, session_id):
        raw_data = self.redis.get(session_id)
        data = {}
        if raw_data:
            self.redis.expire(session_id, self.session_timeout)
            session_data = ujson.loads(raw_data)
        if isinstance(session_data, dict):
            return session_data
        else:
            return {}

    def get(self, request_handler = None):
        session_id, hmac_key = None, None
        if request_handler:
            session_id, hmac_key = map(request_handler.get_secure_cookie,
            ['session_id', 'verification'])
        exists = True
        if not session_id:
            exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac()
        check_hmac = self._generate_hmac(session_id)
        if hmac_key != check_hmac:
            raise InvalidSessionException()
        session = SessionData(session_id, hmac_key)
        if exists:
            session_data = self._fetch(session_id)
            session.update(session_data)
        return session

    def set(self, request_handler, session):
        pass

    def _generate_hmac(self):
        pass

    def _generate_id(self):
        pass


class InvalidSessionException(Exception):
    pass
