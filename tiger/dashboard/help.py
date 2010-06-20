from tiger.content.models import Content


class Step(object):
    conditions = ()
    link = '#'
    
    def __init__(self, site):
        self.site = site

    def is_complete(self):
        return all(condition(self.site) for condition in self.conditions)


class StepBundle(object):
    def __init__(self, site, completeness_attr, *args):
        self.site = site
        self.steps = [step(site) for step in args]
        self._completeness_cache = [
            step.is_complete() for step in self.steps
        ]
        self.completeness_attr = completeness_attr

    def __iter__(self):
        return iter(
            {
                'name': step.name,
                'status': self._get_step_status(i),
                'link': step.link
            }
            for i, step in enumerate(self.steps)
        )

    def is_complete(self):
        already_complete = getattr(self.site, self.completeness_attr)
        if already_complete:
            return True
        if all(self._completeness_cache):
            setattr(self.site, self.completeness_attr, True)
            self.site.save()
            return True
        return False
        

    def _get_step_status(self, idx):
        if self._completeness_cache[idx] is True:
            return 'complete'
        try:
            next = self._completeness_cache[idx + 1] 
        except IndexError:
            next = None
        try:
            prev = self._completeness_cache[idx - 1] 
        except IndexError:
            prev = None
        if not next and prev:
            return 'current'
        return 'incomplete'
        

class StepOne(Step):
    conditions = (
        lambda site: site.lon and site.lat,
    )
    name = 'Add location'
    link = 'http://www.youtube.com/watch?v=vTk6TT7jdLs'
        

class StepTwo(Step):
    conditions = (
        lambda site: site.timeslot_set.count(),
    )
    name = 'Add hours'
    link = 'http://www.youtube.com/watch?v=ORFoWj9YR9c'
        

class StepThree(Step):
    conditions = (
        lambda site: site.item_set.count(),
    )
    name = 'Add menu items'
    link = 'http://www.youtube.com/watch?v=l5Z7bs0DXr4'
        

class StepFour(Step):
    conditions = tuple(
        lambda site: not Content.objects.get(site=site, slug=slug).is_default()
        for slug in Content.CONTENT_TYPES
    )
    name = 'Edit info pages'
        

class StepFive(Step):
    conditions = (
        lambda site: site.menu,
    )
    name = 'Create PDF menu'

def first_steps(site):
    return StepBundle(site, 'walkthrough_complete', StepOne, StepTwo, StepThree, StepFour, StepFive)
