from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.models import (
    Organization, OrganizationMemberTeam, OrganizationMemberType
)
from sentry.testutils import APITestCase


class CreateOrganizationMemberTeamTest(APITestCase):
    def test_can_join_as_statusless_global_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=True,
        )
        team = self.create_team(name='foo', organization=organization)

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.post(path)

        assert resp.status_code == 204

    def test_can_join_as_global_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=True,
        )
        team = self.create_team(name='foo', organization=organization)
        OrganizationMemberTeam.objects.create(
            team=team,
            organizationmember=member_om,
            is_active=False,
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.post(path)

        assert resp.status_code == 201

        omt = OrganizationMemberTeam.objects.get(
            team=team,
            organizationmember=member_om,
        )
        assert omt.is_active

    def test_can_join_as_existing_team_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=False,
            teams=[team],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.post(path)

        assert resp.status_code == 204

    def test_cannot_join_as_non_team_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=False,
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.post(path)

        assert resp.status_code == 400

    def test_can_join_on_open_org(self):
        self.login_as(user=self.user)

        organization = self.create_organization(
            name='foo',
            owner=self.user,
            flags=Organization.flags.allow_joinleave,
        )
        team = self.create_team(name='foo', organization=organization)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=False,
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.post(path)

        assert resp.status_code == 201

        omt = OrganizationMemberTeam.objects.get(
            team=team,
            organizationmember=member_om,
        )
        assert omt.is_active


class DeleteOrganizationMemberTeamTest(APITestCase):
    def test_can_leave_as_statusless_global_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=True,
        )
        team = self.create_team(name='foo', organization=organization)

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.delete(path)

        assert resp.status_code == 204

        assert OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=False,
        ).exists()

    def test_can_leave_as_global_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=True,
        )
        team = self.create_team(name='foo', organization=organization)
        OrganizationMemberTeam.objects.create(
            team=team,
            organizationmember=member_om,
            is_active=True,
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.delete(path)

        assert resp.status_code == 204

        assert OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=False,
        ).exists()

    def test_can_leave_as_existing_team_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=False,
            teams=[team],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.delete(path)

        assert resp.status_code == 204

        assert not OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=True,
        ).exists()

    def test_can_leave_as_non_team_member(self):
        self.login_as(user=self.user)

        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        member_om = self.create_member(
            organization=organization,
            email='foo@example.com',
            type=OrganizationMemberType.MEMBER,
            has_global_access=False,
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(self.user)

        resp = self.client.delete(path)

        assert resp.status_code == 204

        assert not OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=True,
        ).exists()