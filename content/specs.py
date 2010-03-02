from imagekit.specs import ImageSpec 
from imagekit import processors 

# first we define our thumbnail resize processor 
class ResizeThumb(processors.Resize): 
    width = 75 
    height = 75 
    crop = True


class ThumbSpec(ImageSpec):
    access_as = 'thumb'
    pre_cache = True
    processors = [ResizeThumb]


class ResizeSmall(processors.Resize):
    width = 100
    height = 100


class SmallSpec(ImageSpec):
    access_as = 'small'
    pre_cache = True
    processors = [ResizeSmall]


class ResizeMedium(processors.Resize):
    width = 240
    height = 240


class MediumSpec(ImageSpec):
    access_as = 'medium'
    pre_cache = True
    processors = [ResizeMedium]


class ResizeLarge(processors.Resize):
    width = 500
    height = 500


class LargeSpec(ImageSpec):
    access_as = 'large'
    pre_cache = True
    processors = [ResizeLarge]
