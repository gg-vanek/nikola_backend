IMAGE = "image"


class EmailMedia:
    cid: str
    path: str
    media_type: str

    def __init__(self, cid: str, path: str, media_type: str):
        self.cid = cid
        self.path = path
        self.media_type = media_type

    def __hash__(self):
        return hash(self.cid + ":"+ self.path + ":" + self.media_type)

    def __eq__(self, other):
        if not isinstance(other, EmailMedia):
            return False
        return self.cid == other.cid and self.path == other.path and self.media_type == other.media_type
