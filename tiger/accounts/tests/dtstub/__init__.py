import datetime
import sys
from datetimestub import DateStub, DateTimeStub


def set_datetime(dt):
    DateStub.stubbed = DateTimeStub.stubbed = dt
    setattr(datetime, 'date', DateStub)
    setattr(datetime, 'datetime', DateTimeStub)
    sys.modules['datetime'] = datetime
