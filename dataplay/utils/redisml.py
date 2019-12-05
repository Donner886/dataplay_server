from redis import Redis
from dataplay.utils.mongodbDML import RedisUtils
from sanic.log import logger
from dataplay.session.redisSession import RedisSessionInterface
from dataplay.session.session import SessionDict
import ujson


class RedisDML:

    @staticmethod
    def setValue(key):
        try:
            redisSessionInterface = RedisSessionInterface(expiry=60)
            expiry = redisSessionInterface.set_value(key=key,data=ujson.dumps(dict(name='dongdongma22',age=33)))
            return expiry
        except Exception:
            logger.exception('Set key-value error')

    @staticmethod
    def getValue(key):
        try:
            redisSessionInterface = RedisSessionInterface()
            session = ujson.loads(redisSessionInterface.get_value(prefix='',key=key))
            return session
        except Exception:
            logger.exception("Get value error")


if __name__ == '__main__':
    value = RedisDML.getValue('201910121533')
    print(value)
