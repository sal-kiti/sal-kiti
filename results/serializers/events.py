from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.events import Event
from results.models.organizations import Organization
from results.serializers.organizations import OrganizationSerializer


class EventSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for events
    """
    organization_info = OrganizationSerializer(read_only=True, source='organization')
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all())

    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = ['organization',
                                'organization__areas']

    class Meta:
        model = Event
        fields = (
            'id', 'name', 'description', 'date_start', 'date_end', 'location', 'organization', 'organization_info',
            'public', 'locked', 'permissions')

    def validate(self, data):
        """
        Checks permissions to create or modify events.

        Users may create and modify events organized by the clubs they
        represent, unless the event is locked by the staff.
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_('User not authenticated'), 403)
        if 'date_end' in data and 'date_start' in data and data['date_end'] < data['date_start']:
            raise serializers.ValidationError(_('Start date may not be later than End date.'))
        if user.is_superuser or user.is_staff:
            return data
        if (not (self.instance and self.instance.organization.group in user.groups.all()) and
                ('organization' not in data or data['organization'].group not in user.groups.all())):
            raise serializers.ValidationError(_('No permission to alter or create an event.'), 403)
        if ((self.instance and self.instance.locked) or
                ('locked' in data and data['locked'])):
            raise serializers.ValidationError(_('No permission to alter or create a locked event.'), 403)
        return data
