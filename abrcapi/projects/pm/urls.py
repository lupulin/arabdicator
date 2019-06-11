'''
Created on Oct 21, 2012

@author: topher
'''

from abrcapi.projects.pm.api import ProjectResource, UserResource, IssueResource, \
    InvitedUserResource, ResolutionResource, IssueTypeResource, StatusResource, \
    PriorityResource, CommentResource, CreateUserResource, AssignedIssueResource, \
    RequestInvitationResource, MeResource, EventResource, SearchWordsResource, \
    ActivityItemResource, EmailServerResource, IssueUpdateResource, \
    CommentTemplateResource, StaffResource, AttachmentResource
from django.conf.urls.defaults import *
from tastypie.api import Api

v1_api = Api(api_name='pm')
v1_api.register(UserResource())
v1_api.register(ProjectResource())
v1_api.register(IssueResource())
v1_api.register(ResolutionResource())
v1_api.register(IssueTypeResource())
v1_api.register(StatusResource())
v1_api.register(PriorityResource())
v1_api.register(AssignedIssueResource())
v1_api.register(InvitedUserResource())
v1_api.register(CommentResource())
v1_api.register(CreateUserResource())
v1_api.register(RequestInvitationResource())
v1_api.register(MeResource())
v1_api.register(EventResource())
v1_api.register(SearchWordsResource())
v1_api.register(ActivityItemResource())
v1_api.register(EmailServerResource())
v1_api.register(IssueUpdateResource())
v1_api.register(CommentTemplateResource())
v1_api.register(StaffResource())
v1_api.register(AttachmentResource())

urlpatterns = patterns('',
    (r'^$', "abrcapi.projects.pm.views.home"),
    (r'^system/$', 'abrcapi.projects.pm.views.system'),
    (r'^login/$', 'abrcapi.projects.pm.views.loginUser'),
    (r'^logout/$', 'abrcapi.projects.pm.views.logoutUser'),
    (r'^issue_details/(?P<issue_id>\d+)', 'abrcapi.projects.pm.views.issue_details'),
    (r'^comment/add/(?P<issue_id>\d+)', 'abrcapi.projects.pm.views.handle_post_comment'),
    (r'^user_details/(?P<user_id>\d+)', 'abrcapi.projects.pm.views.user_details'),
    (r'^project_details/(?P<project_id>\d+)', 'abrcapi.projects.pm.views.project_details'),
    (r'^event_details/(?P<event_id>\d+)', 'abrcapi.projects.pm.views.event_details'),
    (r'^test/', 'abrcapi.projects.pm.views.test_email_stuff'),
)