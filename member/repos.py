from .models import Member

class MemberRepo(object):
    def create(self, first_name, last_name,):

        member, created = Member.objects.get_or_create(first_name=first_name, last_name=last_name)
        return member

member_repo = MemberRepo()