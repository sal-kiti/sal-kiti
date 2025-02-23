from drf_spectacular.extensions import OpenApiSerializerFieldExtension


class DRYPermissionsFieldFieldFix(OpenApiSerializerFieldExtension):
    """
    Fix for DRYPermissionsField to generate correct schema.
    """

    target_class = "dry_rest_permissions.generics.DRYPermissionsField"

    def map_serializer_field(self, auto_schema, direction):
        return {
            "type": "object",
            "properties": {
                "create": {"type": "boolean"},
                "update": {"type": "boolean"},
                "write": {"type": "boolean"},
                "read": {"type": "boolean"},
            },
        }
