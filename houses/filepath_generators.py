import os


def generate_house_feature_icon_filename(instance, filename: str):
    path = os.path.join('house_features', 'icons', str(instance.name) + '.' + filename.split('.')[-1])
    return path

def generate_house_picture_filename(instance, filename):
    path = os.path.join('houses', 'pictures', str(instance.house.id), filename)
    return path