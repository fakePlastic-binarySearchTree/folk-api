class AntiSpiderException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotExistsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
