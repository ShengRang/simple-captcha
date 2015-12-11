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
        current_data = session_manager.get(request_handler)
        self.session_id, self.hmac_key = current_data.session_id, current_data.hmac_key
        self.update(current_data)

    def save(self):
        self.session_manager.set(self.request_handler, self)


class SessionManager(object):
    def __init__(self, secret, store_options, session_timeout):
        self.secret, self.store_options = secret, store_options
        self.session_timeout = session_timeout
        self.redis = redis.StrictRedis(host=store_options.get('redis_host')
        , port=store_options.get('redis_port')
        , password=store_options.get('redis_pwd'))

    def _fetch(self, session_id):
        raw_data = self.redis.get(session_id)
        data = {}
        session_data = {}
        if raw_data:
            self.redis.expire(session_id, self.session_timeout)
            session_data = ujson.loads(raw_data)
        return session_data

    def get(self, request_handler = None):
        session_id, hmac_key = None, None
        if request_handler:
            session_id, hmac_key = map(request_handler.get_secure_cookie,
            ['session_id', 'verification'])
        exists = True
        if not session_id:
            exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        check_hmac = self._generate_hmac(session_id)
        if hmac_key != check_hmac:
            #raise InvalidSessionException()
            return SessionData(session_id, check_hmac)
        session = SessionData(session_id, hmac_key)
        if exists:
            session_data = self._fetch(session_id)
            session.update(session_data)
        return session

    def set(self, request_handler, session):
        request_handler.set_secure_cookie("session_id", session.session_id)
        request_handler.set_secure_cookie("verification", session.hmac_key)
        session_data = ujson.dumps(session)
        self.redis.setex(session.session_id, self.session_timeout, session_data)

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()

    def _generate_id(self):
        return hashlib.sha256(self.secret + str(uuid.uuid4())).hexdigest()


class InvalidSessionException(Exception):
    pass
