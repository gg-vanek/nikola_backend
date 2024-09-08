IMAGE = "image"
SVG = "svg"


class EmailMedia:
    cid: str
    path: str
    media_type: str

    def __init__(self, cid: str, path: str, media_type: str):
        self.cid = cid
        self.path = path
        self.media_type = media_type
