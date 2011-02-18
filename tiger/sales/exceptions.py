class PaymentGatewayError(Exception):
    pass

class SiteManagementError(Exception):
    pass

class CapExceeded(Exception):
    pass

class SoftCapExceeded(CapExceeded):
    cap_type = 'soft'

class HardCapExceeded(CapExceeded):
    cap_type = 'hard'
