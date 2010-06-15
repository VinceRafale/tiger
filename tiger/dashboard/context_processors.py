from tiger.dashboard.help import first_steps

def walkthrough(request):
    if request.path.startswith('/dashboard'):
        return {'first_steps': first_steps(request.site)}        
    return {}
