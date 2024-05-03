from application import db


class MetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary(), nullable=False)
    url = db.Column(db.String(100))

    def __init__(self, title: str, description: str, image, url: str):
        self.title = title
        self.description = description
        self.image = image
        self.url = url

    def __repr__(self):
        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'image': self.image,
                'url': self.url}
