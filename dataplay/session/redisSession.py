from typing import Callable
from dataplay.session.session import BaseSessionInterface
from redis import Redis
from sanic.log import logger

from dataplay.utils.mongodbDML import RedisUtils


class RedisSessionInterface(BaseSessionInterface):
    def __init__(
        self,
        domain: str = None,
        expiry: int = 2592000,
        httponly: bool = True,
        cookie_name: str = "session",
        prefix: str = "session:",
        sessioncookie: bool = False,
        samesite: str = None,
        session_name: str = "session",
        secure: bool = False,
    ):
        """Initializes a session interface backed by Redis.

        Args:
            redis_getter (Callable):
                Coroutine which should return an asyncio_redis connection pool
                (suggested) or an asyncio_redis Redis connection.
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            prefix (str, optional):
                Memcache keys will take the format of `prefix+session_id`;
                specify the prefix here.
            sessioncookie (bool, optional):
                Specifies if the sent cookie should be a 'session cookie', i.e
                no Expires or Max-age headers are included. Expiry is still
                fully tracked on the server side. Default setting is False.
            samesite (str, optional):
                Will prevent the cookie from being sent by the browser to the
                target site in all cross-site browsing context, even when
                following a regular link.
                One of ('lax', 'strict')
                Default: None
            session_name (str, optional):
                Name of the session that will be accessible through the
                request.
                e.g. If ``session_name`` is ``alt_session``, it should be
                accessed like that: ``request['alt_session']``
                e.g. And if ``session_name`` is left to default, it should be
                accessed like that: ``request['session']``
                Default: 'session'
            secure (bool, optional):
                Adds the `Secure` flag to the session cookie.
        """
        config = RedisUtils.getPoolConfig()
        redis_getter = Redis(host=config['host'], port=config['port'])
        self.redis_getter = redis_getter

        super().__init__(
            expiry=expiry,
            prefix=prefix,
            cookie_name=cookie_name,
            domain=domain,
            httponly=httponly,
            sessioncookie=sessioncookie,
            samesite=samesite,
            session_name=session_name,
            secure=secure,
        )




    def get_value(self, prefix, key):
        try:
            redis_connection =  self.redis_getter
            return  redis_connection.get(prefix + key)
        except Exception:
            logger.error("Initialize the redis connection or get value error when get session value")
        finally:
            self.redis_getter.close()



    def delete_key(self, key):
        try:
            redis_connection = self.redis_getter
            redis_connection.delete([key])
        except Exception:
            logger.error('Initialize the redis connection or delete key/value error')
        finally:
            self.redis_getter.close()




    def set_value(self, key, data):
        try:
            redis_connection = self.redis_getter
            expiry = redis_connection.setex(key, self.expiry, data)
            return expiry
        except Exception:
            logger.error('Initialize the redis connection error or set key value error when set the session value')
        finally:
            self.redis_getter.close()


