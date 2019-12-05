import time
import datetime
import abc
import ujson
import uuid

from dataplay.session.utils import CallbackDict


class SessionDict(CallbackDict):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)

        self.sid = sid
        self.modified = False


class BaseSessionInterface(metaclass=abc.ABCMeta):
    # this flag show does this Interface need request/response middleware hooks

    def __init__(self, expiry, prefix, cookie_name, domain, httponly, sessioncookie, samesite, session_name, secure):
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.sessioncookie = sessioncookie
        self.samesite = samesite
        self.session_name = session_name
        self.secure = secure

    def delete_cookie(self, request, response):
        response.cookies[self.cookie_name] = request[self.session_name].sid

        # We set expires/max-age even for session cookies to force expiration
        response.cookies[self.cookie_name]["expires"] = datetime.datetime.utcnow()
        response.cookies[self.cookie_name]["max-age"] = 0

    @staticmethod
    def calculate_expires(expiry):
        expires = time.time() + expiry
        return datetime.datetime.fromtimestamp(expires)

    def set_cookie_props(self, request, response):
        response.cookies[self.cookie_name] = request[self.session_name].sid
        response.cookies[self.cookie_name]["httponly"] = self.httponly

        # Set expires and max-age unless we are using session cookies
        if not self.sessioncookie:
            response.cookies[self.cookie_name]["expires"] = self._calculate_expires(self.expiry)
            response.cookies[self.cookie_name]["max-age"] = self.expiry

        if self.domain:
            response.cookies[self.cookie_name]["domain"] = self.domain

        if self.samesite is not None:
            response.cookies[self.cookie_name]["samesite"] = self.samesite

        if self.secure:
            response.cookies[self.cookie_name]["secure"] = True

    @abc.abstractmethod
    def get_value(self, prefix: str, sid: str):
        """
        Get value from datastore. Specific implementation for each datastore.

        Args:
            prefix:
                A prefix for the key, useful to namespace keys.
            sid:
                a uuid in hex string
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_key(self, key: str):
        """Delete key from datastore"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_value(self, key: str, data: SessionDict):
        """Set value for datastore"""
        raise NotImplementedError



    def open(self, request) -> SessionDict:
        """
        Opens a session onto the request. Restores the client's session
        from the datastore if one exists.The session data will be available on
        `request.session`.
        Args:
            request (sanic.request.Request):
                The request, which a session will be opened onto.

        Returns:
            SessionDict:
                the client's session data,
                attached as well to `request.session`.
        """
        # 　判断该请求的session id
        sid = request.cookies.get(self.cookie_name)
        # sid = ''
        # reqBody = {}
        # if 'api/uploadModelFile' not in request.url:
        #      reqBody = request.json
        # if reqBody:

        if sid is None:
            sid = uuid.uuid4().hex

        val =self.get_value(self.prefix, sid)
        # 缓存中内容没有过期
        if val is not None:
            data = ujson.loads(val)
            session_dict = SessionDict(data, sid=sid)
            # 缓存中内容已经过期被清除
        else:
            session_dict = SessionDict(sid=sid)

        # attach the session data to the request, return it for convenience
        request.cookies[self.session_name] = sid
        # 将redis缓存的session内容保存在server端的request中，用于判断session的状态
        request[self.session_name] = session_dict
        return session_dict




    def save(self, request, response) -> None:
        if "session" not in request:
            return

        key = self.prefix + request[self.session_name].sid

        val = ujson.dumps(dict(request[self.session_name]))
        self.set_value(key, val)
        self.set_cookie_props(request, response)
