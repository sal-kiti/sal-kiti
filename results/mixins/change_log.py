from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict

from results.middleware.current_user import get_current_user


class LogChangesMixing(object):
    """Logging mixing which writes changes to Django's admin log.

    Logs add, delete and modified fields for all models using a mixin
    and values for the fields defined in the LOG_VALUE_FIELDS setting.
    """
    def __init__(self, *args, **kwargs):
        super(LogChangesMixing, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def changed_fields(self):
        """
        :return: changed field keys
        :rtype: list
        """
        changed_fields = []
        for key in self.diff.keys():
            changed_fields.append(key)
        return changed_fields

    @property
    def diff(self):
        """
        :return: changed data
        :rtype: dict
        """
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def _dict(self):
        """
        :return: instance data
        :rtype: dict
        """
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    def delete(self, *args, **kwargs):
        """
        Save log entry for data deletion
        """
        object_id = self.pk
        user_id = get_current_user().id if get_current_user() else settings.DEFAULT_LOG_USER_ID
        super(LogChangesMixing, self).delete(*args, **kwargs)
        LogEntry.objects.log_action(
            user_id=user_id,
            content_type_id=ContentType.objects.get_for_model(self).pk,
            object_id=object_id,
            object_repr=str(self),
            action_flag=DELETION,
            change_message="Deleted"
        )

    def _add_message(self):
        """
        Create addition message including values for fields specified in settings file

        :return: add messages
        :rtype: list
        """
        add_message = []
        if type(self).__name__ in settings.LOG_VALUE_FIELDS:
            for field in settings.LOG_VALUE_FIELDS[type(self).__name__]:
                if field in self._dict:
                    add_message.append(field + ": " + str(self._dict[field]))
        return add_message

    def _change_message(self):
        """
        Create change message including values for fields specified in settings file

        :return: change messages
        :rtype: list
        """
        change_message = []
        for field in self.changed_fields:
            if (type(self).__name__ in settings.LOG_VALUE_FIELDS and
                    field in settings.LOG_VALUE_FIELDS[type(self).__name__]):
                change_message.append(field + ": " + str(self.diff[field][1]))
            else:
                change_message.append(field)
        return change_message

    def save(self, *args, **kwargs):
        """
        Create a log entry for add or change messages
        """

        action_flag = CHANGE if self.pk else ADDITION
        user_id = get_current_user().id if get_current_user() else settings.DEFAULT_LOG_USER_ID
        super(LogChangesMixing, self).save(*args, **kwargs)
        change_message = []
        if action_flag == ADDITION:
            change_message.append({'added': {}})
            change_message.append({'changed': {'fields': self._add_message()}})
        else:
            if self.changed_fields:
                change_message.append({'changed': {'fields': self._change_message()}})
        if change_message:
            LogEntry.objects.log_action(
                user_id=user_id,
                content_type_id=ContentType.objects.get_for_model(self).pk,
                object_id=self.pk,
                object_repr=str(self),
                action_flag=action_flag,
                change_message=change_message
            )
