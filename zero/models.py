# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.db.models.signals import post_save


from zero.notify import send_notification
from django.dispatch import receiver

import itertools


#TODO multilanguage

#TODO - a pewno do OS !!!!!!
class EntryInfo(models.Model):
    author = models.ForeignKey('auth.User', verbose_name="Author", null=True)
    publication_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('content_type', 'object_id'),)


class EntryInfoMixin(object):

    def get_author(self):
        return self.entry_info.get().author

    def get_publication_datetime(self):
        return self.entry_info.get().publication_datetime

    def get_update_datetime(self):
        return self.entry_info.get().update_datetime

        
class Project(EntryInfoMixin, models.Model):
    verbose_name = models.CharField(max_length=255, verbose_name="Title")
    name = models.SlugField(verbose_name="Machine name")
    description = models.TextField(verbose_name="Description")
    authors = models.ManyToManyField('auth.User', verbose_name="Authors", related_name="projects")
    entry_info = generic.GenericRelation(EntryInfo)    

    default_priority = models.ForeignKey('zero.Priority', verbose_name="Default priority")
    default_status = models.ForeignKey('zero.Status', verbose_name="Default status")
    default_category = models.ForeignKey('zero.Category', verbose_name="Default category")

    def get_authors(self):
        """ Returns auhtors. """
        return self.authors.all()

    def get_subscribers(self):
        return [author.email for author in self.authors.all()]

    def __unicode__(self):
        return u"%s" % self.verbose_name

class Issue(EntryInfoMixin, models.Model):
    verbose_name = models.CharField(max_length=255, verbose_name="Title")
    name = models.SlugField(verbose_name="Name")
    description = models.TextField(verbose_name="Description", blank=True)
    project = models.ForeignKey("Project", verbose_name="Project", related_name="issues")
    dependencies = models.ManyToManyField("Issue", null=True, blank=True, verbose_name="Dependencies", related_name="issues")
    deadline = models.DateField(null=True, blank=True)
    status = models.ForeignKey("Status", verbose_name="Status", related_name="issues")
    priority = models.ForeignKey('Priority', verbose_name="Priority", related_name="issues")
    category = models.ForeignKey('Category', verbose_name="Category", related_name="issues")
    entry_info = generic.GenericRelation(EntryInfo)    

    def get_subscribers(self):
        return [author.email for author in self.project.authors.all()]

    def get_status(self):
        return self.status

    def get_current_status(self):
        """ Zwraca status ustawiony albo przez siebie albo przez najmłodszy komentarz"""
        if self.comments.exists():
            return self.comments.latest('id').status
        return self.status

    def get_priority(self):
        return self.priority

    def get_current_priority(self):
        """ Zwraca status ustawiony albo przez siebie albo przez najmłodszy komentarz"""
        if self.comments.exists():
            return self.comments.latest('id').priority
        return self.priority

    def get_category(self):
        return self.category

    def get_authors(self):
        """ Returns authors of the related project. """
        return self.project.authors.all()

    def __unicode__(self):
        return u"%s" % self.name
    

class Task(EntryInfoMixin, models.Model):
    issue = models.ForeignKey('zero.Issue', verbose_name="Issue", related_name="tasks")
    asignee = models.ForeignKey('auth.User', verbose_name="Assignee", related_name="tasks")
    due_date = models.DateField(verbose_name="Due date", null=True, blank=True)
    due_time = models.TimeField(verbose_name="Due time", null=True, blank=True)
    description = models.TextField(verbose_name="Description", blank=True)
    time_spent = models.PositiveIntegerField(verbose_name="Minutes spent", null=True, blank=True)
    accomplished_date = models.DateField(verbose_name="Accomplished date", null=True, blank=True)
    entry_info = generic.GenericRelation(EntryInfo)    

    def get_title(self):
        return "%s: %s (%s, %s)" % (self.asignee, self.description, self.issue.verbose_name, self.issue.project.verbose_name)

    def get_status(self):
        if self.accomplished_date:
            return 'accomplished'
        return 'pending'

    def get_subscribers(self):
        return [author.email for author in self.issue.project.authors.all()]

#    class Meta:
#        unique_together = (('issue', 'asignee'),)

class BaseIssueState(models.Model):
    verbose_name = models.CharField(max_length=255, verbose_name="Title")
    name = models.SlugField(verbose_name="Name")
    weight = models.IntegerField(verbose_name="Weight")
    
    def __unicode__(self):
        return u"%s" % self.verbose_name
    
    class Meta:
        abstract = True

class Priority(BaseIssueState):
    
    class Meta:
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"
        
class Status(BaseIssueState):
    
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"


class CommentManager(models.Manager):

    def get_latests(self):
        """ Returns latests comments - one per issue. """
        obj = self.all().order_by('issue', '-entry_info__update_datetime')
        ids = [group.next().id for key, group in itertools.groupby(obj, lambda x: x.issue)]
        return self.filter(id__in=ids)

class Comment(EntryInfoMixin, models.Model):
    issue = models.ForeignKey('Issue', verbose_name="Issue", related_name="comments")
    comment = models.TextField(verbose_name="Comment")
    status = models.ForeignKey("Status", verbose_name="Status", related_name="comments")
    priority = models.ForeignKey('Priority', verbose_name="Priority", related_name="comments")
    entry_info = generic.GenericRelation(EntryInfo)    
    objects = CommentManager()

    def get_subscribers(self):
        return [author.email for author in self.issue.project.authors.all()]

class Category(BaseIssueState):

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

# ----------------------------------------------
# 
from pyoss2.middleware import threading
from django.dispatch import receiver

@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Issue)
@receiver(post_save, sender=Project)
@receiver(post_save, sender=Task)
def log_entry(sender, instance, created, using, **kwargs):
    if created or not instance.entry_info.exists():
        ct = ContentType.objects.get_for_model(instance)
        info = EntryInfo.objects.create(author=threading.get_current_user(), content_type=ct, object_id=instance.id)
        # UWAGA BUG:
        # Cannot assign "<django.contrib.auth.models.AnonymousUser object at 0x133e410>": "EntryInfo.author" must be a "User" instance.
        # Przy zapiesie z poziomu anonimowego usera
    else:
        instance.entry_info.get().save()

    send_notification(instance, created)

    
#post_save.connect(log_entry, sender=models.get_model('zero', 'Project'))
#post_save.connect(log_entry, sender=models.get_model('zero', 'Issue'))
#post_save.connect(log_entry, sender=models.get_model('zero', 'Comment'))
