from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create all required user groups for the OMS application'

    def handle(self, *args, **options):
        # List of all groups that need to be created
        groups = [
            'AM',
            'AM_D', 
            'AM_M',
            'EMP',
            'EMP_D',
            'EMP_M',
            'EV',
            'EV_D',
            'EV_M'
        ]
        
        created_count = 0
        existing_count = 0
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created group: {group_name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group already exists: {group_name}')
                )
                existing_count += 1
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'- Created: {created_count} groups\n'
                f'- Already existed: {existing_count} groups\n'
                f'- Total groups: {len(groups)}'
            )
        )
