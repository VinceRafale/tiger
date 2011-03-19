from xml.etree.ElementTree import fromstring, tostring, SubElement, Element
from urllib import quote, urlencode

import httplib2
import md5

OPENSRS_SERVERS = {
        'production': 'https://rr-n1-tor.opensrs.net:55443',
        'test': 'https://horizon.opensrs.net:55443',
        }

OPENSRS_XML_HEADER = "<?xml version='1.0' encoding='UTF-8' standalone='no' ?><!DOCTYPE OPS_envelope SYSTEM 'ops.dtd'>"
OPENSRS_VERSION = '0.9'

class OpenSRSHTTPException(Exception):
    """
    Exception that signals there was an HTTP error during the post to
    the OpenSRS HTTPS API
    """
    pass

class OpenSRSXMLException(Exception):
    """
    Exception that signals there was an error parsing the XML returned
    from the OpenSRS HTTPS API
    """
    pass

class OpenSRS(object):
    """
    Main OpenSRS class.

    The majority of the functionality lies within the post method. It
    turns Python data structures to XML for OpenSRS and then converts
    back the other way for the response.

    Convenience functions exists for some functions, patches are welcome
    """

    H = httplib2.Http()
    server = None
    username = None
    private_key = None

    def __init__(self, username, private_key, test=True):
        """
        Constructor: sets the username, private key and test mode

        Parameters:
        username - your OpenSRS username
        private_key - your OpenSRS private key
        test - set to False for production operation
        """
        self.username = username
        self.private_key = private_key

        key = 'production'
        if test:
            key = 'test'
        self.server = OPENSRS_SERVERS[key]

    def post(self, action, object, attrs, extra_items = {}):
        """
        Post: send an action to the OpenSRS API

        Parameters:
        action - the name of the action (ie. sw_register, name_suggest, etc)
        object - the object type to operate on (ie. domain, trust_service)
        attrs - a data struct to construct the attributes from (see example)
        extra_items - any extra top level items (ie. registrant_ip)

        Example:
        opensrs.post("sw_register", "domain",
            attrs={
                "domain": "example.com",
                "auto_renew": 1,
                "link_domains": 0,
                "reg_type": "new",
                "contact_set": {
                    "owner": { ... },
                    "admin": { ... },
                    "billing": { ... },
                    "tech": { ... },
                    },
                "nameserver_list": [
                    {
                        "sortorder": 1,
                        "name": "ns1.fatbox.ca",
                        },
                    {
                        "sortorder": 2,
                        "name": "ns2.fatbox.ca",
                        },
                    ],
                },
            extra_items = {
                "registrant_ip": "1.2.3.4",
                },
            )
        """

        def xml_to_data(elm, is_list=False):
            """
            This converts an element that has a bunch of 'item' tags
            as children into a Python data structure.

            If is_list is true it is assumed that the child items all
            have numeric indices and should be treated as a list, else
            they are treated as a dict
            """
            if is_list:
                data = []
            else:
                data = {}

            for child in elm:
                if child.tag == 'item':

                    if len(child) > 0:
                        if child[0].tag == 'dt_assoc':
                            new_data = xml_to_data(child[0])
                        elif child[0].tag == 'dt_array':
                            new_data = xml_to_data(child[0], is_list=True)
                    else:
                        new_data = str(child.text)

                    key = child.get('key')
                    if is_list:
                        data.insert(int(key), new_data)
                    else:
                        data[key] = new_data

            return data

        def data_to_xml(elm, key, data):
            """
            data_to_xml adds a item sub element to elm and then sets the
            text if its not a list or dict, otherwise it recurses
            """
            item = SubElement(elm, 'item', { 'key': key })

            if isinstance(data, dict):
                data_to_dt_assoc(item, data)
            elif isinstance(data, list):
                data_to_dt_array(item, data)
            else:
                item.text = str(data)

            return item

        def data_to_dt_assoc(elm, data):
            """
            Adds an associative array of data in the format that opensrs
            requires, uses data_to_xml to recurse
            """
            _dt_assoc = SubElement(elm, 'dt_assoc')
            for key in data.keys():
                data_to_xml(_dt_assoc, key, data[key])

        def data_to_dt_array(elm, list):
            """
            Adds an list of data in the format that opensrs requires,
            uses data_to_xml to recurse
            """
            _dt_array = SubElement(elm, 'dt_array')
            key = 0
            for ent in list:
                data_to_xml(_dt_array, str(key), ent)
                key += 1

        # build our XML structure
        env = Element("OPS_envelope")

        # add the header
        header = SubElement(env, 'header')
        version = SubElement(header, 'version')
        version.text = str(OPENSRS_VERSION)

        # add the body
        body = SubElement(env, 'body')
        data_block = SubElement(body, 'data_block')
        data_to_dt_assoc(data_block, {
            'protocol': 'XCP',
            'action': action,
            'object': object,
            'attributes': attrs,
            })

        data = "%s%s" % (OPENSRS_XML_HEADER, tostring(env))

        # create our signature:
        # MD5(MD5(data + private_key)+private_key)
        signature = md5.new("%s%s" % (md5.new("%s%s" % (data, self.private_key)).hexdigest(), self.private_key)).hexdigest()

        # send our post
        resp, content = self.H.request(self.server, "POST", 
                body=data,
                headers={
                    'Content-Type': 'text/xml',
                    'X-Username': self.username,
                    'X-Signature': signature,
                    'Content-Length': str(len(data)),
                    })

        if resp.status == 200:
            # parse the XML response
            dom = fromstring(content)

            # check the version
            version = dom.find('header/version')
            if version == None:
                raise OpenSRSXMLException("Response did not contain a version")
            if version.text > OPENSRS_VERSION:
                raise OpenSRSXMLException("Response version is newer than we understand! Response: %s -- Supported: %s" % (version.text, OPENSRS_VERSION))

            # find our response data
            data_block = dom.find('body/data_block/dt_assoc')
            if data_block == None:
                raise OpenSRSXMLException("Response did not contain valid data (could not find body/data_block/dt_assoc)")

            # convert
            data = xml_to_data(data_block)

            return data
        else:
            raise OpenSRSHTTPException("Status returned from POST was not 200")


    def name_suggest(self, query, tlds=[".COM", ".NET", ".ORG", ".INFO", ".BIZ", ".US", ".MOBI"]):
        """
        Shortcut for the name_suggest function
        """
        return self.post("name_suggest", "domain", {
            "searchstring": query,
            "max_wait_time": 3,
            "tlds": tlds,
            })
