from django.utils.translation import ugettext_lazy as _
from drf_queryfields import QueryFieldsMixin
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.models.categories import CategoryForCompetitionType
from results.models.results import Result, ResultPartial
from results.serializers.athletes import AthleteLimitedSerializer, AthleteNameSerializer
from results.serializers.competitions import CompetitionLimitedSerializer, CompetitionResultTypeLimitedSerializer
from results.serializers.records import RecordLimitedSerializer
from results.mixins.eager_loading import EagerLoadingMixin


class ResultPartialSerializer(serializers.ModelSerializer):
    """
    Serializer for partial results
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = ResultPartial
        fields = ('id', 'result', 'type', 'order', 'value', 'decimals', 'code', 'time', 'text', 'permissions')
        extra_kwargs = {'code': {'required': False}}

    def validate(self, data):
        """
        Validates:
         - permissions to create or edit the partial result
         - value limits
        """
        if (not (self.context['request'].user.is_superuser or self.context['request'].user.is_staff) and
            ((self.instance and (self.instance.result.competition.locked or self.instance.result.approved)) or
                data['result'].competition.locked or data['result'].approved or
                data['result'].competition.organization.group not in self.context['request'].user.groups.all())):
            raise serializers.ValidationError(_('No permission to alter or create a record.'), 403)
        if data['type'].competition_type != data['result'].competition.type:
            raise serializers.ValidationError(_('Partial result type does not match competition type.'))
        if ('value' in data and data['result'] and data['type'].min_result is not None and
                data['value'] < data['type'].min_result):
            raise serializers.ValidationError(_('A result is too low.'))
        if data['result'] and data['type'].max_result:
            max_result = data['type'].max_result
            category = data['result'].category
            if category.team and category.team_size:
                max_result = max_result * category.team_size
            if 'value' in data and data['value'] > max_result:
                raise serializers.ValidationError(_('A result is too high.'))
        return data


class ResultPartialNestedSerializer(ResultPartialSerializer):
    """
    Serializer for nested partial result updates where validation is done in results serializer
    """
    class Meta:
        model = ResultPartial
        fields = ('id', 'type', 'order', 'value', 'decimals', 'code', 'time', 'permissions')
        extra_kwargs = {'code': {'required': False}}

    def validate(self, data):
        return data


class ResultSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    """
    Serializer for results
    """
    dry_run = serializers.BooleanField(required=False)
    partial = ResultPartialNestedSerializer(many=True, required=False)
    permissions = DRYPermissionsField()

    class Meta:
        model = Result
        fields = (
            'id', 'competition', 'athlete', 'team_members', 'first_name', 'last_name', 'organization', 'category',
            'elimination_category', 'result', 'decimals', 'result_code', 'position', 'position_pre',
            'approved', 'info', 'team', 'partial', 'permissions', 'dry_run')

    def create(self, validated_data):
        """
        Nested partial results support in create
        """
        partial_data = validated_data.pop('partial', None)
        team_members = validated_data.pop('team_members', None)
        dry_run = validated_data.pop('dry_run', None)
        if not dry_run:
            result = Result.objects.create(**validated_data)
        else:
            result = Result(**validated_data)
        if partial_data:
            for partial in partial_data:
                if not dry_run:
                    ResultPartial.objects.create(result=result, **partial)
        if team_members and not dry_run:
            result.team_members.set(team_members)
        return result

    def update(self, instance, validated_data):
        """
        Nested partial results support in update
        """
        dry_run = validated_data.pop('dry_run', None)
        if not dry_run:
            for data in validated_data:
                if data not in ['partial', 'team_members']:
                    setattr(instance, data, validated_data[data])
            if 'team_members' in validated_data:
                team_members = validated_data.pop('team_members')
                instance.team_members.set(team_members)
            instance.save()
            partial_existing = list(ResultPartial.objects.filter(result=instance).values_list('id', flat=True))
            if 'partial' in validated_data:
                partial_data = validated_data.pop('partial')
                for partial in partial_data:
                    try:
                        partial_instance = ResultPartial.objects.get(result=instance,
                                                                     type=partial['type'],
                                                                     order=partial['order'])
                        for data in partial:
                            if data not in ['result', 'type', 'order']:
                                setattr(partial_instance, data, partial[data])
                        partial_instance.save()
                        partial_existing.remove(partial_instance.pk)
                    except ResultPartial.DoesNotExist:
                        ResultPartial.objects.create(result=instance, **partial)
                ResultPartial.objects.filter(pk__in=partial_existing).delete()
        return instance

    @staticmethod
    def _age_difference(competition, athlete, exact):
        """
        Returns athlete's age at the time of competition.
        """
        if exact:
            return competition.date_start.year - athlete.date_of_birth.year -\
                   ((competition.date_start.month, competition.date_start.day) <
                    (athlete.date_of_birth.month, athlete.date_of_birth.day))
        else:
            return competition.date_start.year - athlete.date_of_birth.year

    def _check_max_age(self, competition, category, athlete):
        """
        Validates athletes maximum age
        """
        if (athlete.date_of_birth and
                ((not category.age_exact and
                  self._age_difference(competition, athlete, category.age_exact) > category.max_age)
                 or (category.age_exact and
                     self._age_difference(competition, athlete, category.age_exact) >= category.max_age))):
            raise serializers.ValidationError(_("Athlete is too old for this category."))

    def _check_min_age(self, competition, category, athlete):
        """
        Validates athletes minimum age
        """
        if (athlete.date_of_birth and
                self._age_difference(competition, athlete, category.age_exact) < category.min_age):
            raise serializers.ValidationError(_("Athlete is too young for this category."))

    def _check_age(self, competition, category, athletes):
        """
        Validates category's age requirements.
        """
        if category.min_age:
            for athlete in athletes:
                self._check_min_age(competition, category, athlete)
        if category.max_age:
            for athlete in athletes:
                self._check_max_age(competition, category, athlete)

    @staticmethod
    def _check_gender(category, athletes):
        """
        Validates category's gender requirement.
        """
        for athlete in athletes:
            if ((category.gender == "W" and athlete.gender == "M") or
                    (category.gender == "M" and athlete.gender == "W")):
                raise serializers.ValidationError(_("Athlete's gender is not allowed for this category."))

    @staticmethod
    def _check_number_of_team_members(category, athletes):
        """
        Validates the number of team members.
        """
        if category.team and category.team_size and len(athletes) != category.team_size:
            raise serializers.ValidationError(_("Incorrect number of team members for this category."))

    @staticmethod
    def _check_requirements(competition, athletes):
        """
        Validates competition level and type requirements for the athletes.
        i.e. licence.
        """
        for requirement in competition.type.requirements.split(',') + competition.level.requirements.split(','):
            if requirement.strip():
                for athlete in athletes:
                    if not athlete.organization.external and not athlete.info.filter(
                            type=requirement.strip(),
                            date_start__lte=competition.date_start,
                            date_end__gte=competition.date_start).count():
                        raise serializers.ValidationError(_("Missing requirement: %s." % requirement.strip()))

    def _check_value_limits(self, result, category, competition_type):
        """
        Validates result total limits.
        """
        max_result, min_result = self._get_result_limits(category, competition_type)
        if category.team and category.team_size and max_result:
            max_result = max_result * category.team_size
        if min_result is not None and result < min_result:
            raise serializers.ValidationError(_('A result is too low.'))
        if max_result is not None and result > max_result:
            raise serializers.ValidationError(_('A result is too high.'))

    @staticmethod
    def _check_team(data):
        """
        Validates team information.
        """
        if 'team' in data and data['team'] and not data['category'].team:
            raise serializers.ValidationError(_("Incorrect category for a team result."))
        if 'athlete' in data and data['athlete'] and data['category'].team:
            raise serializers.ValidationError(_("Use team_members instead of athlete field for teams."))
        if 'team_members' not in data and data['category'].team:
            raise serializers.ValidationError(_("Team result without team_members."))

    def _get_category(self, data):
        """
        Returns the result category in data or old instance.
        """
        if 'category' in data:
            category = data['category']
        elif self.instance:
            category = self.instance.category
        else:
            raise serializers.ValidationError(_("Missing category."))
        return category

    def _get_athletes(self, data):
        """
        Returns the list of athletes in a result and if a result is team.
        """
        athletes = []
        if (self.instance and self.instance.team) or ('team' in data and data['team']):
            team = True
            if 'team_members' in data:
                athletes = data['team_members']
            elif self.instance:
                athletes = self.instance.team_members.all()
            else:
                raise serializers.ValidationError(_("Missing athletes."))
        else:
            team = False
            if 'athlete' in data and data['athlete']:
                athletes = [data['athlete']]
            elif self.instance:
                athletes = [self.instance.athlete]
        if not athletes:
            raise serializers.ValidationError(_("Missing athletes."))
        return athletes, team

    def _get_competition(self, data):
        """
        Returns the competition in data or old instance.
        """
        if 'competition' in data:
            competition = data['competition']
        elif self.instance:
            competition = self.instance.competition
        else:
            raise serializers.ValidationError(_("Missing competition."))
        return competition

    def _get_result(self, data):
        """
        Returns the result total in data or old instance.
        """
        if 'result' in data:
            result = data['result']
        elif self.instance:
            result = self.instance.result
        else:
            result = None
        return result

    @staticmethod
    def _get_result_limits(category, competition_type):
        """
        Returns result limits for the competition type and category.

        Raises ValidationError if category is not allowed for the competition
        type.
        """
        check = CategoryForCompetitionType.objects.filter(category=category, type=competition_type).first()
        if check and check.disallow:
            raise serializers.ValidationError(_("Category is not allowed for this competition type."))
        max_result = check.max_result if check and check.max_result else competition_type.max_result
        min_result = check.min_result if check and check.min_result else competition_type.min_result
        return max_result, min_result

    def _check_existence(self, data, category):
        """
        Raises ValidationError if trying to create new result and it already exists.
        """
        if self.instance is None and (
                (not category.team and Result.objects.filter(competition=data['competition'],
                                                             athlete=data['athlete'],
                                                             category=data['category'])) or
                (category.team and Result.objects.filter(competition=data['competition'],
                                                         last_name=data['last_name'],
                                                         category=data['category']))):
            raise serializers.ValidationError(_('Entry already exists.'))

    def _check_team_status(self, data):
        """
        Raises ValidationError if team status is changed. This is done because of the validation and record checks.
        """
        if self.instance and (('team' in data and data['team'] and not self.instance.team) or
                              (self.instance.team and 'team' in data and not data['team'])):
            raise serializers.ValidationError(_('Cannot change team status.'))

    @staticmethod
    def _check_partial(data, competition, category):
        """
        Validate partial results
        """
        if 'partial' in data and len(data['partial']):
            for partial in data['partial']:
                if partial['type'].competition_type != competition.type:
                    raise serializers.ValidationError(_('Partial result type does not match competition type.'))
                if 'value' in partial and partial['type'].min_result is not None and partial['value'] < partial['type'].min_result:
                    raise serializers.ValidationError(_('A result is too low.'))
                if 'value' in partial and partial['type'].max_result is not None:
                    max_result = partial['type'].max_result
                    if category.team and category.team_size:
                        max_result = max_result * category.team_size
                    if partial['value'] > max_result:
                        raise serializers.ValidationError(_('A result is too high.'))

    def validate(self, data):
        """
        Validates:
         - permissions to create or modify the result
         - team status
         - duplicates
         - competition level and type requirements for the athlete
         - number of team members in result
         - gender limitations for the category
         - age limitations for the category
         - value limits for the result
         - partial results
        """
        if (not (self.context['request'].user.is_superuser or self.context['request'].user.is_staff) and
            ((self.instance and
              (self.instance.competition.locked or self.instance.approved or
               (self.instance.competition.level.require_approval and not self.instance.competition.approved))) or
                (data['competition'].locked or
                 (data['competition'].level.require_approval and not data['competition'].approved) or
                 ('approved' in data and data['approved']) or
                 data['competition'].organization.group not in self.context['request'].user.groups.all()))):
            raise serializers.ValidationError(_('No permission to alter or create a record.'), 403)
        self._check_team_status(data)
        athletes, team = self._get_athletes(data)
        category = self._get_category(data)
        competition = self._get_competition(data)
        self._check_existence(data, category)
        self._check_requirements(competition, athletes)
        self._check_number_of_team_members(category, athletes)
        self._check_gender(category, athletes)
        self._check_age(competition, category, athletes)
        result = self._get_result(data)
        if result is not None:
            self._check_value_limits(result, category, competition.type)
        self._check_partial(data, competition, category)
        if 'approved' in data and data['approved'] and not (self.context['request'].user.is_superuser or
                                                            self.context['request'].user.is_staff):
            raise serializers.ValidationError(_("No permission to approve results."))
        return data


class ResultPartialLimitedSerializer(ResultPartialSerializer):
    """
    Serializer for partial results with limited information
    """

    type = CompetitionResultTypeLimitedSerializer(read_only=True)

    class Meta:
        model = ResultPartial
        fields = ('id', 'type', 'order', 'value', 'decimals', 'code', 'time', 'text')


class ResultLimitedSerializer(QueryFieldsMixin, serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for limited result information
    """
    athlete = AthleteLimitedSerializer(read_only=True)
    team_members = AthleteNameSerializer(read_only=True, many=True)
    competition = CompetitionLimitedSerializer(read_only=True)
    partial = ResultPartialLimitedSerializer(many=True, read_only=True)
    record = RecordLimitedSerializer(many=True, read_only=True)

    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    elimination_category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    organization = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )

    _PREFETCH_RELATED_FIELDS = ['athlete',
                                'athlete__info',
                                'athlete__organization',
                                'athlete__organization__areas',
                                'athlete__additional_organizations',
                                'category',
                                'competition',
                                'competition__event',
                                'competition__level',
                                'competition__organization',
                                'competition__organization__areas',
                                'competition__type',
                                'organization',
                                'elimination_category',
                                'partial',
                                'partial__type',
                                'record',
                                'record__level',
                                'record__category',
                                'team_members'
                                ]

    class Meta:
        model = Result
        fields = (
            'id', 'athlete', 'first_name', 'last_name', 'team_members', 'competition', 'organization', 'category',
            'elimination_category', 'result', 'result_code', 'decimals', 'position', 'position_pre', 'partial',
            'approved', 'team', 'info', 'record')


class ResultLimitedAggregateSerializer(ResultLimitedSerializer):
    """
    Serializer for limited aggregate result information
    """
    _PREFETCH_RELATED_FIELDS = ['athlete',
                                'athlete__organization',
                                'athlete__organization__areas',
                                'athlete__additional_organizations',
                                ]

    class Meta:
        model = Result
        fields = ('id', 'athlete', 'result')
