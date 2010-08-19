from datetime import date, datetime

class BaseStub(object):
    stubbed = None

    @classmethod
    def today(cls):
        return cls.stubbed.date()

    def __getattr__(self, name):
        return super(BaseStub, self).__getattr__(name)


class DateStub(date, BaseStub):
    pass


class DateTimeStub(datetime, BaseStub):
    @classmethod
    def now(cls):
        return cls.stubbed

    @classmethod
    def time(cls):
        return cls.stubbed.time()
