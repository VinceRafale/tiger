class OrderingError(Exception):
    def __init__(self, msg, redirect_to):
        """docstring for init"""
        self.msg = msg
        self.redirect_to = redirect_to


class NoOnlineOrders(OrderingError):
    pass


class ClosingTimeBufferError(OrderingError):
    pass


class RestaurantNotOpen(OrderingError):
    pass

    
class ItemNotAvailable(OrderingError):
    pass

    
class SectionNotAvailable(OrderingError):
    pass


class PricePointNotAvailable(OrderingError):
    pass
