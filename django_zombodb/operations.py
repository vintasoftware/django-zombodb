from django.contrib.postgres.operations import CreateExtension


class ZomboDBExtension(CreateExtension):

    def __init__(self):
        self.name = 'zombodb'
