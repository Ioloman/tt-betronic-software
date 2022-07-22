import typing

from models import HasID


class DummyDB(list):
    def add(self, obj: HasID):
        self.append(obj)

    def get_all(self):
        return self.copy()

    def get(self, id_: str) -> typing.Optional[HasID]:
        for elem in self:
            if elem.get_id() == id_:
                return elem.copy()
        else:
            return None

    def update(self, id_: str, obj: HasID) -> bool:
        for i in range(len(self)):
            if self[i].get_id() == id_:
                self[i] = obj
                return True
        else:
            return False
