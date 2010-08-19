import datetime as datetime_orig


class datetime(datetime_orig.datetime):

    @classmethod
    def now(cls):
        """Override the datetime.now() method to return a
        datetime one year in the future
        """
        result = datetime_orig.datetime.now()
        return result.replace(year=result.year + 1)

class MockDatetime(object):
    """A datetimestub object to replace methods and classes from 
    the datetime module. 

    Usage:
        import sys
        sys.modules['datetime'] = DatetimeStub()
    """

    def __getattr__(self, attr):
        """Get the default implementation for the classes and methods
        from datetime that are not replaced
        """
        return getattr(datetime_orig, attr)

