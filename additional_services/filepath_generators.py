import os


def generate_additional_service_picture_filename(instance, filename):
    path = os.path.join('additional_services', 'pictures', str(instance.additional_service.id), filename)
    return path
