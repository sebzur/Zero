# -*- coding: utf-8 -*-
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.db.models import get_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django import  forms
from django.template.defaultfilters import slugify


from synergy.templates.regions.views import RegionViewMixin

class CreateProjectView(RegionViewMixin, CreateView):
    model = get_model('zero','Project')

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateProjectView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "New project"
        return ctx
    
    def get_success_url(self):
        return reverse('list_projects')

class UpdateProjectView(RegionViewMixin, UpdateView):
    """ Handle project issue updates. """
    model = get_model('zero', 'Project')

    def get_success_url(self):
        return reverse('list_project_issues', args=[self.object.id])
     
    def _get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero','Issue')
                exclude = ( 'project',)
        return IssueForm

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateProjectView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Update information on %s" % self.get_object()
        ctx['navlinks'] = {'Project': reverse('list_project_issues', args=[self.get_object().id]),
                           'Delete': reverse('delete_object', args=['project', self.get_object().id]),
                           }

        return ctx

        
# --------------------------------------------
# Views classes handling project issues
# -------------------------------------------
class CreateProjectIssueView(RegionViewMixin, CreateView):
    """ Handle project issue creation. """
#    template_name = 'zero/edit/issue.html'

    def get_success_url(self):
        return reverse('list_project_issues',args=[self.kwargs.get('proj_id')])

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateProjectIssueView, self).get_context_data(*args, **kwargs)
        project = self.get_project()
        ctx['title'] = "Create issue for %s" % project
        ctx['navlinks'] = {'Project': reverse('list_project_issues', args=[project.id]),
                           }
        return ctx

     
    def get_initial(self):
        project = self.get_project()
        return  dict([(field, getattr(project, 'default_%s' % field).id) for field in ('status', 'category', 'priority')])

    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            assign_task = forms.BooleanField(required=False)

            class Meta:
                model = get_model('zero','Issue')
                exclude = ( 'project', 'name')
        return IssueForm
        

    def get_project(self):
        return get_model('zero', 'project').objects.get(id=self.kwargs.get('proj_id'))
    
    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.project_id = self.kwargs.get('proj_id')
        self.object.name = slugify(self.kwargs.get('title'))
        self.object.save()
        if form.cleaned_data.get('assign_task'):
            get_model('zero', 'Task').objects.create(issue=self.object, asignee=self.request.user)
        return HttpResponseRedirect(self.get_success_url())

class UpdateProjectIssueView(RegionViewMixin, UpdateView):
    """ Handle project issue updates. """
    model = get_model('zero','Issue')
#    template_name = 'zero/edit/issue.html'

    def get_success_url(self):
        return reverse('issue_details', args=[self.object.id])
     
    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero','Issue')
                exclude = ( 'project',)
        return IssueForm
        
    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateProjectIssueView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Update issue %s" % self.get_object()
        ctx['navlinks'] = {'Project': reverse('list_project_issues', args=[self.get_object().project.id]),
                           'Delete': reverse('delete_object', args=['issue', self.get_object().id]),
                           }

        return ctx


class CreateIssueCommentView(RegionViewMixin, CreateView):
    #model = get_model('zero','Issue')
    #template_name = 'zero/edit/comment.html'
    #form_class = get_form()
        
    def get_success_url(self):
        return reverse('issue_details', args=[self.kwargs.get('issue_id')])
     
    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero','Comment')
                exclude = ( 'issue',)
        return IssueForm

    def get_initial(self):
        return {'status': self.get_issue().get_current_status(), 'priority': self.get_issue().get_current_status()}

    def get_issue(self):
        return get_model("zero", "issue").objects.get(id=self.kwargs.get('issue_id'))

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateIssueCommentView, self).get_context_data(*args, **kwargs)
        issue = self.get_issue()
        ctx['title'] = "Comment for %s" % issue
        ctx['navlinks'] = {'Project': reverse('list_project_issues', args=[issue.project.id]),
                           'Issue': reverse('issue_details', args=[issue.id]),
                           }

        return ctx

    def form_valid(self, form):
        
        self.object = form.save(commit = False)
        self.object.issue_id = self.kwargs.get('issue_id')
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
        #return super(CreateIssueCommentView, self).form_valid(form)


class UpdateCommentView(RegionViewMixin, UpdateView):
    """ Handle project issue updates. """
    model = get_model('zero', 'Comment')

    def get_success_url(self):
        return reverse('issue_details', args=[self.object.issue.id])
     
    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero','Comment')
                exclude = ('issue', )
        return IssueForm

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateCommentView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Comment for %s" % self.get_object().issue
        ctx['navlinks'] = {'Issue': reverse('issue_details', args=[self.get_object().issue.id]),
                           }

        return ctx


class CreateTaskView(RegionViewMixin, CreateView):
    #model = get_model('zero','Issue')
    #form_class = get_form()
        
    def get_success_url(self):
        return reverse('issue_details', args=[self.kwargs.get('issue_id')])

    def get_initial(self):
        return {'asignee': self.request.user}
     
    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero', 'Task')
                exclude = ( 'issue',)
        return IssueForm

    def get_issue(self):
        return get_model("zero", "issue").objects.get(id=self.kwargs.get('issue_id'))
        
    def form_valid(self, form):
        
        self.object = form.save(commit = False)
        self.object.issue_id=self.kwargs.get('issue_id')
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateTaskView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Task for for %s" % self.get_issue()
        ctx['navlinks'] = {'Issue': reverse('issue_details', args=[self.get_issue().id]),
                           }

        return ctx

class UpdateTaskView(RegionViewMixin, UpdateView):
    """ Handle project issue updates. """
    model = get_model('zero', 'Task')

    def get_success_url(self):
        return reverse('issue_details', args=[self.object.issue.id])
     
    def get_form_class(cls):
        class IssueForm(forms.ModelForm):
            class Meta:
                model = get_model('zero','Task')
                exclude = ('issue', )
        return IssueForm

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateTaskView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Update task %s" % self.get_object()
        ctx['navlinks'] = {'Issue': reverse('issue_details', args=[self.get_object().issue.id]),
                           }

        return ctx


class DeleteObjectView(DeleteView):
    template_name = 'zero/edit/confirm_delete.html'

    def get_queryset(self):
        """
        Get the queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        self.model = get_model('contenttypes','ContentType').objects.get(model=self.kwargs.get('model')).model_class()
        return super(DeleteView, self).get_queryset()

    def get_success_url(self):
        reverse_names = {'issue': ('list_project_issues', 'project_id'),
                         'comment': ('issue_details', 'issue_id'),
                         'task': ('issue_details', 'issue_id'),
                         'project': ('list_projects', None)
                         }
        if reverse_names[self.kwargs.get('model')][1]:
            attr = getattr(self.object, reverse_names[self.kwargs.get('model')][1])
            return reverse(reverse_names[self.kwargs.get('model')][0], args=[attr])
        return reverse(reverse_names[self.kwargs.get('model')][0])


    def get_context_data(self, **kwargs):
        context = super(DeleteObjectView, self).get_context_data(**kwargs)

        # Templete is provided with the URL that should be used if the user wants to
        # cancel the delete decision.
        # -----------------
        
        reverse_names = {'issue': ('issue_details', 'id'),
                         'comment': ('issue_details', 'issue_id'),
                         'project': ('list_project_issues', 'id'),
                         'task': ('issue_details', 'issue_id'),
                         }
        attr = getattr(self.object, reverse_names[self.kwargs.get('model')][1])
        context['cancel_url'] = reverse(reverse_names[self.kwargs.get('model')][0], args=[attr])

        return context
