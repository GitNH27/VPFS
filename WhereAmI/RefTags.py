from typing import Dict

class ReferenceTag:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


refTags: Dict[int, ReferenceTag] = { }

def _addTag(tag: ReferenceTag):
    refTags[tag.id] = tag

# Currently just one tag, ID 0, placed at origin
_addTag(ReferenceTag(0, 0, 0))