# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.db.models import get_model
from django.shortcuts import get_object_or_404

from synergy.templates.regions.views import RegionViewMixin

from django.core.urlresolvers import reverse

class IssueView(RegionViewMixin, DetailView):
    model = get_model('zero','Issue')

    def get_context_data(self, *args, **kwargs):
        ctx = super(IssueView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Issue: %s" % self.get_object().verbose_name
        ctx['navlinks'] = {'Project': reverse('list_project_issues', args=[self.get_object().project.id]),
                           'Edit': reverse('edit_issue', args=[self.get_object().id]),
                           'Delete': reverse('delete_object', args=['issue', self.get_object().id]),
                           }
        return ctx
