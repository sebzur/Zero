# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from zero.views import lists, edit, details

urlpatterns = patterns('',
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'pageone/login.html'}, name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
                       # Dashboard
                       url(r'^dashboard/(?P<model>issue|comment)/$', lists.Dashboard.as_view(), name='dashboard'),
                       # Project
                       url(r'^projects/$', lists.ProjectsView.as_view(), name='list_projects'),
                       url(r'^project/(?P<pk>\d+)/edit/$', edit.UpdateProjectView.as_view(), name="edit_project"),
                       url(r'^project/create/$', edit.CreateProjectView.as_view(), name='create_project'),
                       url(r'^project/(?P<proj_id>\d+)/issues/$', lists.ProjectIssuesView.as_view(), name='list_project_issues'),
                       url(r'^project/(?P<proj_id>\d+)/issues/create/$', edit.CreateProjectIssueView.as_view(), name='create_project_issue'),
                       # Issue
                       url(r'^issue/(?P<pk>\d+)/$', details.IssueView.as_view(), name="issue_details"),
                       #url(r'^issues/(?P<project>[\w-]+)/(?P<status>[\w-]+)/(?P<priority>[\w-]+)/(?P<category>[\w-]+)/(?P<author>[\w-]+)/(?P<assignee>[\w-]+)/$', lists.FilteredIssuesView.as_view(),
                       #    defaults={'project': 'all', 'status': 'all', 'priority': 'all', 'category': 'all', 'author': 'all', 'assignee': 'all'}, name="filtered_issues"),
                       url(r'^issues/$', lists.FilteredIssuesView.as_view(), name="filtered_issues"),
                       url(r'^issue/(?P<pk>\d+)/edit/$', edit.UpdateProjectIssueView.as_view(), name="edit_issue"),
                       url(r'^issue/(?P<issue_id>\d+)/comments/create/$', edit.CreateIssueCommentView.as_view(), name="create_issue_comment"),
                       url(r'^comment/(?P<pk>\d+)/edit/$', edit.UpdateCommentView.as_view(), name="edit_comment"),
                       url(r'^issue/(?P<issue_id>\d+)/tasks/create/$', edit.CreateTaskView.as_view(), name="create_task"),
                       url(r'^task/(?P<pk>\d+)/edit/$', edit.UpdateTaskView.as_view(), name="edit_task"),
                       # TASK
                       url(r'^tasks/(?P<status>open|closed)/$', lists.TasksView.as_view(), name='list_tasks'),
                       # Generic handlers
                       url(r'^delete/(?P<model>.+)/(?P<pk>\d+)/$', edit.DeleteObjectView.as_view(), name="delete_object"),
)

