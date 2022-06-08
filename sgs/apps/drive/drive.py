__author__ = 'Yevhenii Dits'


from sgs.apps.services import DriveService, Storage


class Drive(DriveService):

    def __init__(self):
        super().__init__()
        self._my_storage = None

    @property
    def my_storage(self):
        if not self._my_storage:
            self._my_storage = Storage()
        return self._my_storage

