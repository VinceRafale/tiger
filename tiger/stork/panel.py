from component import ComponentGroup, get_component

class Panel(object):
    components = []

    def __init__(self, stork, **data):
        self.stork = stork
        self.name = data['name']
        self.admonition = data.pop('admonition', None)
        try:
            self.component_type = data['type']
        except KeyError:
            self.groups = [ComponentGroup(self, **g) for g in data['groups']]
        else:
            self.component = get_component(self, None, data)

    def __iter__(self):
        return iter(self.groups)
