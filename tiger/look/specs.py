from imagekit.specs import ImageSpec 
from imagekit import processors 

# first we define our thumbnail resize processor 
class ResizeLogo(processors.Resize): 
    width = 620 
    height = 200 
    crop = True


class LogoSpec(ImageSpec):
    access_as = 'resized'
    pre_cache = True
    processors = [ResizeLogo]
