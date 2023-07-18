import redis

'''
redis-14305.c252.ap-southeast-1-1.ec2.cloud.redislabs.com:14305
HongKongPolytechnicUniversity-free-db
Redis CRUD 
RedisJSON type data
'''


class RedisDB:
    # Should change to your RedisDB setting
    __settings = {
        "host": "localhost",
        # "host": "redis-14305.c252.ap-southeast-1-1.ec2.cloud.redislabs.com",
        # "port": 14305,
        "port": 6379,
        "db": 0,
        # "password": "jQjuqKtA3RtaMu7ARYoh2KLFhQqlUHFb",
        "decode_responses": True
    }

    def __init__(self):
        self.rds = redis.Redis(**self.__settings)

    def getFull(self, key):
        return self.rds.json().get(key, '$')

    def get(self, key, path):
        return self.rds.json().get(key, '$' + path)

    def getlist(self, k):
        return self.rds.lrange(k, 0, -1)


    def set(self, key, value):
        self.rds.json().set(key, '$', value)

    def setlist(self, k, v):
        self.rds.rpush(k, v)

    def remove(self, key):
        self.rds.delete(key)

    # @property change foo.func() ---> foo.func
    @property
    def keys(self):
        return self.rds.keys()
    # flush data

    @property
    def flushdb(self):
        return self.rds.flushdb()

    @property
    def isEmpty(self):
        return self.rds.dbsize() == 0
