# -*- coding: utf-8 -*-
from django.views.generic import ListView, TemplateView
from django.db.models import get_model, Q
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.views.generic.edit import FormView, FormMixin, BaseFormView, ProcessFormView
from zero import forms
from django.utils.encoding import smart_unicode, smart_str 

from synergy.templates.regions.views import RegionViewMixin

import itertools

class ProjectsView(RegionViewMixin, ListView):
    model = get_model('zero','Project')

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProjectsView, self).get_context_data(*args, **kwargs)
        ctx['title'] = 'Projects list'
        ctx['navlinks'] = {'Add new project': reverse('create_project')}
        return  ctx

class ProjectIssuesView(RegionViewMixin, ListView):
    
    def get_queryset(self):
        queryset=get_model('zero','Issue').objects.filter(project__id__exact=self.kwargs.get('proj_id'))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        project = get_object_or_404(get_model('zero','Project'), id__exact=self.kwargs.get('proj_id'))
        context = super(ProjectIssuesView, self).get_context_data(**kwargs)
        context['project'] = project
        context['title'] = "Project %s issues" % project
        context['navlinks'] = {'Create Issue': reverse('create_project_issue', args=[project.id]),
                               'Edit': reverse('edit_project', args=[project.id]),
                               #'Delete': reverse('delete_object', args=['project', project.id]),
                               }
        return context

        
class TasksView(RegionViewMixin, ListView):
    model = get_model('zero', 'Task')

    def _get_queryset(self):
        queryset = super(TasksView, self).get_queryset().filter(asignee=self.request.user)
        name = self.kwargs.get('status')

        latests_comments = get_model('zero', 'Comment').objects.get_latests()

        all_commented_issues = latests_comments.values_list('issue', flat=True)
        commented_issues_by_status = latests_comments.filter(status__name=name).values_list('issue', flat=True)

        with_comments = queryset.filter(issue__in=commented_issues_by_status).values_list('id', flat=True)

        without_comments = queryset.exclude(issue__in=all_commented_issues).filter(issue__status__name=name).values_list('id', flat=True)


        queryset = queryset.filter(id__in=itertools.chain(with_comments, without_comments))

        return queryset

    def get_queryset(self):
        is_open = {'open': True, 'closed': False}.get(self.kwargs.get('status'))
        return super(TasksView, self).get_queryset().filter(asignee=self.request.user, accomplished_date__isnull=is_open)
        
    def get_context_data(self, **kwargs):
        context = super(TasksView, self).get_context_data(**kwargs)
        context['title'] = "Tasks list"
        filters = dict(('%s' % status, reverse('list_tasks', args=[status.lower()]))  for status in ('Open', 'Closed'))
        context['navlinks'] = filters
        return context

        
class FilteredIssuesView(RegionViewMixin, BaseFormView, ListView):
    #template_name = 'zero/lists/filtered_issues.html'
    form_class = forms.IssueFilter
    model = get_model('zero', 'Issue')

    def get_from_list(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        context = self.get_context_data(object_list=self.object_list)
        return context
        #return self.render_to_response(context)

    def get_from_form(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.get_context_data(form=form)
        #return self.render_to_response(self.get_context_data(form=form))

    def _get_context_data(self, *args, **kwargs):
        frm = self.get_from_list(request=None, *args, **kwargs)
        lst = self.get_from_form(request=None, *args, **kwargs)
        lst.update(frm)
        lst.update({'title': 'Filtered issues'})
        return lst

    def get(self, request, *args, **kwargs):
        print request.POST
        return self.render_to_response(self._get_context_data(*args, **kwargs))

    def form_invalid(self, form):
        return self.render_to_response(self._get_context_data(form=form))

    def get_form_kwargs(self):
        z = super(FilteredIssuesView, self).get_form_kwargs()
        return z

    def get_success_url(self, get):
        base = reverse('filtered_issues')
        if get:
            return "%s?%s" % (base, get)
        return base

    def form_valid(self, form):
        get = form.get_encoded_cleaned_data()
        print 'CLEANED:', form.cleaned_data
        return HttpResponseRedirect(self.get_success_url(get))

    def get_initial(self):
        # KURWA, w jakis wyjatkowo dziwny sposob, ktorego nie moge skumac,
        # jezeli zostawie self.initial nie 'wyzerowane', to mi pamieta...
        self.initial = {}
        GET = dict(((k, v) for k, v in self.request.GET.iteritems() if k in self.get_form_class().FIELDS.keys() and v != 'none'))
        FIELDS = self.get_form_class().FIELDS
        if GET:
            for field, value in GET.iteritems():
                if field in (u'author', u'assigned'):
                    print 'AUTH'
                    self.initial[field] = get_model('auth', 'User').objects.get(username=value)
                else:
                    self.initial[field] = get_model('zero', field).objects.get(**{FIELDS[field]: value})
        return self.initial

    def get_queryset(self):
        quer = self.get_initial()
        ids = []
        if quer.has_key('author'):
            user = quer.pop('author')
            ids = get_model('zero','EntryInfo').objects.filter(author=user, content_type__model='issue').only('object_id').values_list('object_id', flat=True)
            quer['id__in'] = ids
        # Python dict keys have to be strings (not unicodes!)
        d = dict( (smart_str("%s" % key), value) for key, value in quer.iteritems())
        return super(FilteredIssuesView, self).get_queryset().filter(**d)
        
        
class Dashboard(RegionViewMixin, TemplateView):

    def get_objects(self):
        return get_model('zero', self.kwargs.get('model')).objects.all().order_by('-entry_info__publication_datetime')[:10]

    def get_context_data(self, *args, **kwargs):
        ctx = super(Dashboard, self).get_context_data(*args, **kwargs)
        ctx['title'] = 'Dashboard.'
        ctx['navlinks'] = {'Issues': reverse('dashboard', args=['issue']),
                           'Comments': reverse('dashboard', args=['comment']),
                           }
        ctx['objects'] = self.get_objects()
        ctx['region_postfixes'] = {'managedcontent': self.kwargs.get('model')}
        return  ctx
