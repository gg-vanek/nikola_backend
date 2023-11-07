from rest_framework.permissions import AllowAny


class ByActionMixin:

    permission_classes_by_action = {
        "default": [AllowAny],
    }

    serializer_classes_by_action = {
        "default": None,
    }

    def get_serializer_class(self):
        serializer_class = self.serializer_classes_by_action.get(self.action,
                                                                 self.serializer_classes_by_action["default"])
        return serializer_class

    def get_permissions(self):
        permission_classes = self.permission_classes_by_action.get(self.action,
                                                                   self.permission_classes_by_action["default"])
        return [permission() for permission in permission_classes]
