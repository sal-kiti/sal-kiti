from django.db.models.signals import post_save
from django.dispatch import receiver

from divari.models import Season, Team, TeamResult


@receiver(post_save, sender=Season)
def copy_teams(sender, instance=None, created=False, **kwargs):
    """Copy teams from the previous season when created."""
    if created:
        season = Season.objects.filter(date_end__lt=instance.date_start).order_by("-date_end").first()
        teams = Team.objects.filter(season=season)
        for team in teams:
            if TeamResult.objects.filter(team=team).count() >= season.result_count:
                Team.objects.get_or_create(
                    season=instance,
                    bow_type=team.bow_type,
                    organization=team.organization,
                    number=team.number,
                    defaults={"division": team.division},
                )
