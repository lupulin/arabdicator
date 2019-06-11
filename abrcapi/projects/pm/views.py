from abrcapi.projects.pm.models import Issue, Project, Event, Comment, Status
from abrcapi.projects.pm.utils import handle_uploaded_file
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.files.uploadedfile import UploadedFile
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import timezone, log
from email.Parser import Parser as EmailParser
from email.header import decode_header
from email.utils import parseaddr
import StringIO
import email

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/pm/system/')
    c = {}
    c.update(csrf(request))
    return render_to_response('home.html', c)

@login_required(login_url="/pm/")
def system(request):
    c = {}
    c.update(csrf(request))
    user = request.user
    issues = Issue.objects.filter(Q(reporter=user) | Q(assignees=user) | Q(project__lead=user)).distinct()
    c["user"] = user
    c["issues"] = issues
    return render_to_response('dashboard.html', c)

def loginUser(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            request.session['user']=user.pk
            return HttpResponseRedirect("/pm/system/")
        else:
            return HttpResponseRedirect("/pm/")
    else:
        return HttpResponseRedirect("/pm/")
        pass
    
@login_required(login_url="/pm/")
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/pm/")

@login_required(login_url="/pm/")
def issue_details(request, issue_id):
    c = {}
    c.update(csrf(request))
    issue = Issue.objects.get(pk=issue_id)
    c["issue"] = issue
    c["comments"] = issue.comments.all().order_by('-pub_date')
    c["attachments"] = issue.attachment_set.all()
    return render_to_response('issue_details.html', c)

@login_required(login_url="/pm/")
def handle_post_comment(request, issue_id):
    if request.POST:
        c = {}
        c.update(csrf(request))
        attachments = request.FILES.getlist('attachments')
        staff_only = request.POST.get('staff_only')
        print staff_only
        comment = request.POST.get('comment')
        issue = Issue.objects.get(pk=issue_id)
        curUser = request.user
        if staff_only:
            added_comment = Comment.objects.create(issue=issue, commenter=curUser, comment=comment, only_staff=True)
        else:
            added_comment = Comment.objects.create(issue=issue, commenter=curUser, comment=comment)
        for a in attachments:
            attachment = UploadedFile(a)
            handle_uploaded_file(attachment, issue)
        status = Status.objects.get(name="In Progress")
        issue.status = status
        issue.save()
    return HttpResponseRedirect('/pm/issue_details/'+issue_id)

@login_required(login_url="/pm/")
def user_details(request, user_id):
    c = {}
    c.update(csrf(request))
    user = User.objects.get(pk=user_id)
    issues = Issue.objects.filter(Q(reporter=user) | Q(assignees=user) | Q(project__lead=user)).distinct()
    c["user"] = user
    c["issues"] = issues
    c["logged"] = request.user
    return render_to_response('user_details.html', c)

@login_required(login_url="/pm/")
def project_details(request, project_id):
    c = {}
    c.update(csrf(request))
    project = Project.objects.get(pk=project_id)
    c["project"] = project
    c["user"] = request.user
    return render_to_response('project_details.html', c)

@login_required(login_url="/pm/")
def event_details(request, event_id):
    c = {}
    c.update(csrf(request))
    event = Event.objects.get(pk=event_id)
    localTime = timezone.localtime(event.date)
    c["user"] = request.user
    if request.user in event.attendees.all():
        going = True
    else:
        going = False
    c["going"] = going
    c["date"] = localTime.strftime("%m/%d/%y")
    c["time"] = localTime.strftime("%I:%M %p")
    c["event"] = event
    return render_to_response('event_details.html', c)
            
@login_required(login_url="/pm/")
def test_email_stuff(request):
    c = {}
    c.update(csrf(request))
    
    # TODO: get email and put it in a list we can then output
    import imaplib, email, re, base64
    from urllib2 import unquote
    from BeautifulSoup import BeautifulSoup
    
    imap = imaplib.IMAP4_SSL("SERVER", PORT)
    imap.login("EMAIL_ADDRESS", "PASSWORD")
    imap.select()
    
    emailList = []
    imgSrcs = []
    
    typ, data = imap.search(None, "ALL")
    data = data[0].split()
    
    for num in data:
        typ, emailData = imap.fetch(num, '(RFC822)')
        msgobj = email.message_from_string(emailData[0][1])
        for part in msgobj.walk():
            content_type = part.get_content_type()
            payload = part.get_payload()
            imageMatch = re.search("image/\w+", content_type)
            if imageMatch is not None:
                encoding = part.get("Content-Transfer-Encoding")
                imgSrc = "data:"+content_type+";"+encoding+","+payload
                imgSrcs.append(imgSrc)
        count = 0
        for part in msgobj.walk():
            if part.get_content_type() == "text/html":
                soup = BeautifulSoup(str(part.get_payload(decode=True)))
                if len(imgSrcs) != 0:
                    for img in soup.findAll('img'):
                        img['src'] = imgSrcs[count]
                        count+=1
                emailList.append(str(soup))
                imgSrcs = []
                
    c["email"] = emailList
    return render_to_response('test_temp.html', c)
