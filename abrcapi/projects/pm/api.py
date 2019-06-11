'''
Created on Oct 21, 2012

@author: topher
'''
from abrcapi.projects.pm.EmailServices import EmailServices
from abrcapi.projects.pm.models import Project, Issue, IssueType, Status, \
    Resolution, InvitedUsers, Priority, Comment, Event, EmailServer, SearchWord, \
    Item, IssueUpdate, CommentTemplate, Attachment
from abrcapi.projects.pm.utils import sendTemplateEmail, fullName, IssueUpdater, \
    createNewIssueUpdate
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.cache import SimpleCache
from tastypie.constants import ALL
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.exceptions import BadRequest, NotFound, ApiFieldError
from tastypie.fields import ToManyField
from tastypie.resources import ModelResource, Resource
from tastypie.throttle import CacheDBThrottle

class UserResource(ModelResource):
    """
    UserResource provides some amount of data about users
    in the system.
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['first_name', 'last_name', 'email', 'username', 'id']
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        filtering = {
            "username": ('exact', 'startswith')
        }
        
    def dehydrate(self, bundle):
        user = User.objects.get(username=bundle.obj.username)
        if user.first_name == "Anonymous":
            formattedUser = user.email
        else:
            formattedUser = fullName(bundle.obj)
        bundle.data["formatted_user"] = formattedUser
        return bundle
        
class StaffResource(ModelResource):
    """
    """
    class Meta:
        queryset = User.objects.filter(groups__name="pm_staff")
        resource_name = 'staff'
        fields = ['first_name', 'last_name', 'email', 'username', 'id']
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        filtering = {
            "username": ('exact', 'startswith')
        }
        
    def dehydrate(self, bundle):
        user = User.objects.get(username=bundle.obj.username)
        formattedUser = fullName(bundle.obj)
        bundle.data["formatted_user"] = formattedUser
        return bundle
        
class EmailServerResource(ModelResource):
    
    class Meta:
        allowed_methods = ['get', 'put']
        queryset = EmailServer.objects.all()
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        resource_name = "emailserver"
        
        
class CreateUserResource(ModelResource):
    """
    Separate ModelResource that handles user creation.
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'usercreate'
        fields = ['first_name', 'last_name', 'email', 'username', 'id']
        allowed_methods = ['post']
        authorization = Authorization()
        filtering = {
            "username": ('exact', 'startswith')
        }
 
    def obj_create(self, bundle, request=None, **kwargs):
        invitedUser = None
        try:
            invitedUser = InvitedUsers.objects.get(email=bundle.data.get('email'), accepted=True)
        except:
            raise BadRequest(u"You haven't been invited")
        try:
            staff_group = Group.objects.get(name="pm_staff")
            try:
                anonymousUser = User.objects.get(email=bundle.data.get('email'))
                anonymousUser.set_password(bundle.data.get('password'))
                anonymousUser.username = bundle.data.get('username')
                anonymousUser.first_name = bundle.data.get('first_name')
                anonymousUser.last_name = bundle.data.get('last_name')
                anonymousUser.groups.add(staff_group)
                anonymousUser.save()
            except:
                bundle = super(CreateUserResource, self).obj_create(bundle, request, **kwargs)
                bundle.obj.set_password(bundle.data.get('password'))
                bundle.obj.groups.add(staff_group)
                bundle.obj.save()
            invitedUser.delete()
        except:
            raise BadRequest(u"Oops! Maybe somebody already took that username")
        return bundle

class ProjectResource(ModelResource):
    """
    ProjectResource gives information about projects. A 
    supervisor is required.
    """
    lead = fields.ForeignKey(UserResource, 'lead', full=True)
    issues = fields.ToManyField("abrcapi.projects.pm.api.IssueResource", "issues", null=True)
    
    class Meta:
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        queryset = Project.objects.all()
        resource_name = "project"
        filtering = {
            'name': ALL,
            'lead': ALL,
            'status': ALL,
        }
        
    def dehydrate(self, bundle):
        issues = Issue.objects.filter(project=bundle.obj)
        openIssueCount = len(issues)
        bundle.data["issueCount"] = openIssueCount
        bundle.data["obj_type"] = "project"
        bundle.data["project_id"] = bundle.obj.pk
        return bundle

class SearchWordsResource(ModelResource):
    
    project = fields.ForeignKey(ProjectResource, 'project')
    
    class Meta:
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        queryset = SearchWord.objects.all()
        resource_name = "words"
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        filtering = {
            'project': ALL,
        }
      
class IssueTypeResource(ModelResource):
    fields = ["name", "description"]
    
    class Meta:
        queryset = IssueType.objects.all()
        authorization = DjangoAuthorization()
        resource_name = "issuetype"
        filtering = {
            'name': ALL,
        }

class StatusResource(ModelResource):
    fields = ["name", "description"]
    class Meta:
        queryset = Status.objects.all()
        authorization = DjangoAuthorization()
        resource_name = "status"
        filtering = {
            'name': ALL,
        }
        
class PriorityResource(ModelResource):
    fields = ["name", "description"]
    class Meta:
        queryset = Priority.objects.all()
        authorization = DjangoAuthorization()
        resource_name = "priority"
        filtering = {
            'name': ALL,
        }
        
class ResolutionResource(ModelResource):
    fields = ["name", "description"]
    class Meta:
        queryset = Resolution.objects.all()
        authorization = DjangoAuthorization()
        resource_name = "resolution"
        filtering = {
            'name': ALL,
        }
      
class AssignedIssueResource(ModelResource):
    status = fields.ForeignKey(StatusResource, 'status', full=True, null=True)
    project = fields.ForeignKey(ProjectResource, 'project', full=True)
    resolution = fields.ForeignKey(ResolutionResource, 'resolution', full=True, null=True)
    priority = fields.ForeignKey(PriorityResource, 'priority', full=True, null=True)
    watchers = fields.ToManyField(UserResource, 'watchers', full=True, null=True)
    type = fields.ForeignKey(IssueTypeResource, 'type', null=True, full=True)
    reporter = fields.ForeignKey(UserResource, 'reporter', full=True, null=True)
    assignees = fields.ToManyField(UserResource, 'assignees', full=True, null=True)
    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(Q(reporter=request.user) | Q(assignees=request.user) | Q(project__lead=request.user)).distinct()
    
    class Meta:
        queryset = Issue.objects.all().order_by('-pub_date')
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        resource_name = 'assigned'
        filtering = {
            'name': ALL,
            'date_created': ALL,
            'status': ALL,
            'resolution': ALL,
            'priority': ALL,
            'type': ALL,
            'reporter': ALL,
            'assignees': ALL,
            'project': ALL,
            'description': ALL,
            'query': ALL
        }
        
    def apply_filters(self, request, applicable_filters):
        base_object_list = super(AssignedIssueResource, self).apply_filters(request, applicable_filters)
        
        query = request.GET.get('query', None)
        if query:
            qset = (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(resolution__name__icontains=query) |
                Q(status__name__icontains=query) |
                Q(priority__name__icontains=query) |
                Q(type__name__icontains=query) |
                Q(project__name__icontains=query) |
                Q(project__description__icontains=query)
            )
            base_object_list = base_object_list.filter(qset).distinct()
        return base_object_list
        
    def obj_update(self, bundle, request=None, **kwargs):
        
        acting_user = User.objects.get(pk=request.user.id)
        
        old_assignees = []
        try:
            for x in bundle.obj.assignees.all():
                if x.first_name == "Anonymous":
                    old_assignees.append(x.email)
                else:
                    old_assignees.append(x.first_name+" "+x.last_name)
        except:
            pass
        bundle.obj.last_user = request.user
        
        oldResolution = bundle.obj.resolution.name
        oldPriority = bundle.obj.priority.name
        oldStatus = bundle.obj.status.name
        oldType = bundle.obj.type.name
        
        # Functionality to keep track of new project.
        oldProject = bundle.obj.project.id
        
        bundle = super(AssignedIssueResource, self).obj_update(bundle, request, **kwargs)
        new_assignees = []
        print "Trying to compare new and old updates..."
        if bundle.obj.resolution.name != oldResolution:
            if bundle.obj.resolution.name != "Fixed":
                createNewIssueUpdate(bundle.obj, "resolution", oldResolution, bundle.obj.resolution.name, acting_user)
        if bundle.obj.priority.name != oldPriority:
            createNewIssueUpdate(bundle.obj, "priority", oldPriority, bundle.obj.priority.name, acting_user)
        if bundle.obj.status.name != oldStatus:
            createNewIssueUpdate(bundle.obj, "status", oldStatus, bundle.obj.status.name, acting_user)
        if bundle.obj.type.name != oldType:
            createNewIssueUpdate(bundle.obj, "issue type", oldType, bundle.obj.type.name, acting_user)
        try:
            for x in bundle.obj.assignees.all():
                if x.first_name == "Anonymous":
                    new_assignees.append(x.email)
                else:
                    new_assignees.append(x.first_name+" "+x.last_name)
        except:
            pass
        
        # Determine if project is different
        if bundle.obj.project.id != oldProject:
            # set emailed to False
            issue = Issue.objects.get(pk=bundle.obj.pk)
            issue.emailed = False
            issue.save()
        
        removed = list(set(old_assignees) - set(new_assignees))
        added = list(set(new_assignees) - set(old_assignees))
        for assignee in removed:
            createNewIssueUpdate(bundle.obj, "assignee", "removed", assignee, acting_user)
        for assignee in added:
            createNewIssueUpdate(bundle.obj, "assignee", "added", assignee, acting_user)
        return bundle
        
    def obj_create(self, bundle, request=None, **kwargs):
        acting_user = User.objects.get(pk=request.user.id)
        bundle.obj.last_user = acting_user
        bundle = super(AssignedIssueResource, self).obj_create(bundle, request, **kwargs)
        return bundle
        
    def dehydrate(self, bundle):
        project = bundle.obj.project
        bundle.data["assignee-count"] = len(bundle.obj.assignees.all())
        bundle.data["issue_key"] = project.key+"-"+str(bundle.obj.id)
        bundle.data["issue_id"] = bundle.obj.pk
        bundle.data["obj_type"] = "issue"
        return bundle
      
class IssueResource(ModelResource):
    status = fields.ForeignKey(StatusResource, 'status', full=True, null=True)
    project = fields.ForeignKey(ProjectResource, 'project', full=True)
    resolution = fields.ForeignKey(ResolutionResource, 'resolution', full=True, null=True)
    priority = fields.ForeignKey(PriorityResource, 'priority', full=True, null=True)
    watchers = fields.ToManyField(UserResource, 'watchers', full=True, null=True)
    type = fields.ForeignKey(IssueTypeResource, 'type', null=True, full=True)
    reporter = fields.ForeignKey(UserResource, 'reporter', full=True, null=True)
    comments = fields.ToManyField("abrcapi.projects.pm.api.CommentResource", "comments", null=True)
    assignees = fields.ToManyField(UserResource, 'assignees', full=True, null=True)
    
    class Meta:
        queryset = Issue.objects.all().order_by('-pub_date')
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        allowed_methods = ['get', 'patch', 'post', 'put']
        resource_name = 'issue'
        cache = SimpleCache(timeout=10)
        filtering = {
            'name': ALL,
            'date_created': ALL,
            'status': ALL,
            'resolution': ALL,
            'priority': ALL,
            'type': ALL,
            'reporter': ALL,
            'assignees': ALL,
            'project': ALL,
            'description': ALL,
            'query': ALL
        }
        
    def apply_filters(self, request, applicable_filters):
        base_object_list = super(IssueResource, self).apply_filters(request, applicable_filters)
        
        query = request.GET.get('query', None)
        user = request.GET.get('user', None)
        if query:
            qset = (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(resolution__name__icontains=query) |
                Q(status__name__icontains=query) |
                Q(priority__name__icontains=query) |
                Q(type__name__icontains=query) |
                Q(project__name__icontains=query) |
                Q(project__description__icontains=query)
            )
            base_object_list = base_object_list.filter(qset).distinct()
        if user:
            qset = (
                Q(reporter=user) |
                Q(assignees__in=user)
            )
            base_object_list = base_object_list.filter(qset).distinct()
        return base_object_list
        
    def obj_update(self, bundle, request=None, **kwargs):
        
        acting_user = User.objects.get(pk=request.user.id)
        
        old_assignees = []
        try:
            for x in bundle.obj.assignees.all():
                if x.first_name == "Anonymous":
                    old_assignees.append(x.email)
                else:
                    old_assignees.append(x.first_name+" "+x.last_name)
        except:
            pass
        bundle.obj.last_user = acting_user
        
        oldResolution = bundle.obj.resolution.name
        oldPriority = bundle.obj.priority.name
        oldStatus = bundle.obj.status.name
        oldType = bundle.obj.type.name
        
        # Functionality to keep track of new project.
        oldProject = bundle.obj.project.id
        
        bundle = super(IssueResource, self).obj_update(bundle, request, **kwargs)
        new_assignees = []
        
        if bundle.obj.resolution.name != oldResolution:
            if bundle.obj.resolution.name != "Fixed":
                createNewIssueUpdate(bundle.obj, "resolution", oldResolution, bundle.obj.resolution.name, acting_user)
        if bundle.obj.priority.name != oldPriority:
            createNewIssueUpdate(bundle.obj, "priority", oldPriority, bundle.obj.priority.name, acting_user)
        if bundle.obj.status.name != oldStatus:
            createNewIssueUpdate(bundle.obj, "status", oldStatus, bundle.obj.status.name, acting_user)
        if bundle.obj.type.name != oldType:
            createNewIssueUpdate(bundle.obj, "issue type", oldType, bundle.obj.type.name, acting_user)
        try:
            for x in bundle.obj.assignees.all():
                if x.first_name == "Anonymous":
                    new_assignees.append(x.email)
                else:
                    new_assignees.append(x.first_name+" "+x.last_name)
        except:
            pass
        
        # Determine if project is different
        if bundle.obj.project.id != oldProject:
            # set emailed to False
            issue = Issue.objects.get(pk=bundle.obj.pk)
            issue.emailed = False
            issue.save()
            
        
        removed = list(set(old_assignees) - set(new_assignees))
        added = list(set(new_assignees) - set(old_assignees))
        for assignee in removed:
            createNewIssueUpdate(bundle.obj, "assignee", "removed", assignee, acting_user)
        for assignee in added:
            createNewIssueUpdate(bundle.obj, "assignee", "added", assignee, acting_user)
        return bundle
        
    def obj_create(self, bundle, request=None, **kwargs):
        acting_user = User.objects.get(pk=request.user.id)
        bundle.last_user = acting_user
        bundle = super(IssueResource, self).obj_create(bundle, request, **kwargs)
        return bundle
    
    def dehydrate(self, bundle):
        project = bundle.obj.project
        bundle.data["assignee-count"] = len(bundle.obj.assignees.all())
        bundle.data["issue_key"] = project.key+"-"+str(bundle.obj.id)
        bundle.data["issue_id"] = bundle.obj.pk
        bundle.data["obj_type"] = "issue"
        return bundle
        
class CommentResource(ModelResource):
    issue = fields.ForeignKey(IssueResource, 'issue')
    commenter = fields.ForeignKey(UserResource, 'commenter')
    
    class Meta:
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'delete', 'patch']
        queryset = Comment.objects.all()
        resource_name = 'comment'
        
    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(CommentResource, self).obj_create(bundle, request, **kwargs)
        try:
            print bundle.obj.issue
            issue = bundle.obj.issue
            print "Attempting to change issue status..."
            inProgress = Status.objects.get(pk=2)
            if issue.status.name != inProgress:
                issue.status = inProgress
                issue.save()
        except Exception, e:
            print "issue could not be changed to 'In Progress'..."
            print e
        return bundle
    
    def dehydrate(self, bundle):
        bundle.data["obj_type"] = "issue"
        bundle.data["issue_id"] = bundle.obj.issue.pk
        return bundle
    
class CommentTemplateResource(ModelResource):
    class Meta:
        authorization = Authorization()
        authentication = SessionAuthentication()
        allowed_methods = ['get', 'post', 'delete', 'put']
        queryset = CommentTemplate.objects.all()
        resource_name = 'template'
        
class InvitedUserResource(ModelResource):
    class Meta:
        queryset = InvitedUsers.objects.all()
        resource_name = 'invite'
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
        filtering = {
            'accepted': ALL,
        }
    
    # obj_update -- accept invitation
    def obj_update(self, bundle, request, **kwargs):
        accepted = bundle.data.get('accepted')
        if accepted:
            admin = "Arabdicator Admin" + "<" + EmailServer.objects.get(type="INCOMING").email + ">"
            sendTemplateEmail("email/invite_request_accepted.txt", "You have been accepted!", admin, bundle.obj)
        return super(InvitedUserResource, self).obj_update(bundle, request, **kwargs)
    
    # obj_delete -- reject invitation
    def obj_delete(self, request=None, **kwargs):
        try:
            obj = self.obj_get(request, **kwargs)
            admin = "Arabdicator Admin" + "<" + EmailServer.objects.get(type="INCOMING").email + ">"
            sendTemplateEmail("email/invite_request_rejected.txt", "Oh no! Bad news", admin, obj)
        except ObjectDoesNotExist:
            raise NotFound("A model instance matching the provided arguments could not be found.")
        return super(InvitedUserResource, self).obj_delete(request, **kwargs)
    
class RequestInvitationResource(ModelResource):
    class Meta:
        queryset = InvitedUsers.objects.all()
        resource_name = 'request'
        authorization = Authorization()
        allowed_methods = ["post"]
        
    def obj_create(self, bundle, request, **kwargs):
        bundle = super(RequestInvitationResource, self).obj_create(bundle, request, **kwargs)
        admin = "Arabdicator Admin" + "<" + EmailServer.objects.get(type="INCOMING").email + ">"
        sendTemplateEmail("email/invitation_request.txt", "Thank you for your request!", admin, bundle.obj)
        return bundle
        
class PermissionResource(ModelResource):
    class Meta:
        queryset = Permission.objects.all()
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        
class GroupResource(ModelResource):
    permissions = fields.ManyToManyField(PermissionResource, 'permissions', full=True, null=True)
    class Meta:
        queryset = Group.objects.all()
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        
class EventResource(ModelResource):
    attendees = fields.ManyToManyField(UserResource, 'attendees', full=True, null=True)
    class Meta:
        queryset = Event.objects.all().order_by('date')
        allowed_methods = ['post', 'get', 'put', 'delete', 'patch']
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        resource_name = 'event'
        filtering = {
            'name': ALL,
            'date': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
    def dehydrate(self, bundle):
        bundle.data["obj_type"] = "event"
        bundle.data["event_id"] = bundle.obj.pk
        return bundle
        
class IssueUpdateResource(ModelResource):
    
    class Meta:
        queryset = IssueUpdate.objects.all()
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        resource_name = 'update'
        
    def dehydrate(self, bundle):
        bundle.data["issue_id"] = bundle.obj.issue.pk
        bundle.data["obj_type"] = "issue"
        return bundle
        
class MeResource(ModelResource):
    groups = fields.ManyToManyField(GroupResource, 'groups', full=True, null=True)
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(username=request.user.username)
    
    def dehydrate(self, bundle):
        user = User.objects.get(username=bundle.obj.username)
        formattedUser = fullName(bundle.obj)
        bundle.data["formatted_user"] = formattedUser
        return bundle
    
    class Meta:
        queryset = User.objects.all()
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        excludes = ['password']
        allowed_methods = ['get', 'post', 'delete', 'put', 'patch']
        resource_name = 'me'
        
class ActivityItemResource(ModelResource):
    content_object = GenericForeignKeyField({
        Project: ProjectResource,
        Event: EventResource,
        Issue: IssueResource,
        Comment: CommentResource,
        IssueUpdate: IssueUpdateResource
    }, 'content_object', full=True)
        
    class Meta:
        resource_name = 'activity'
        queryset = Item.objects.all().order_by('-pub_date')
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        cache = SimpleCache(timeout=10)
        
    def dehydrate(self, bundle):
        item = bundle.obj.content_object
        bundle.data["summary"] = item.__unicode__()
        return bundle
    
class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(MultipartResource, self).deserialize(request, data, format)
    
class AttachmentResource(MultipartResource, ModelResource):
    """
    Attachment Resource
    """
    class Meta:
        resource_name="attachment"
        allowed_methods = ['get', 'post', 'delete']
        queryset = Attachment.objects.all()
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        