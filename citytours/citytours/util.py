from werkzeug import import_string, cached_property


def simplified_keys(project):
    sps = list(project.find_statepoints())
    varied_keys = list()
    for key in sps[0]:
        same_for_all = True  # This key has the same value for all statepoints
        for sp in sps:
            if sps[0][key] != sp[key]:
                same_for_all = False
                break
        if not same_for_all:
            varied_keys.append(key)
    return varied_keys


def ellipsis_string(string, length=60):
    string = str(string)
    half = int(length / 2)
    if len(string) < length:
        return string
    else:
        return string[:half] + "..." + string[-half:]


class LazyView(object):

    def __init__(self, citytour, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name
        self.citytour = citytour

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        kwargs.update({'citytour': self.citytour})
        return self.view(*args, **kwargs)
