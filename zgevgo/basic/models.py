import hashlib
from django.utils import timezone
from django.db import models
from django.dispatch import receiver


class ShaField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 40)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('db_index', True)
        super(ShaField, self).__init__(*args, **kwargs)


class Stream(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


@receiver(models.signals.post_save, sender=Stream)
def create_initial_action(instance, created, **kwargs):
    if not created:
        return

    action = Action(
        stream=instance,
        author=Author.objects.get_or_create(name='sys')[0],
        parent_sha='init',
        message='init'
    )
    action.save(initial_action=True)


class Author(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name


class Action(models.Model):
    stream = models.ForeignKey(Stream)
    author = models.ForeignKey(Author)
    self_sha = ShaField()
    parent_sha = ShaField()
    timestamp = models.DateTimeField()

    message = models.TextField()

    def save(self, **kwargs):
        initial_action = kwargs.pop('initial_action', False)
        if self.id:
            raise Exception('resaving an Action is not allowed')
        self.timestamp = timezone.now()
        if not initial_action:
            if not self.parent_sha:
                # raise Exception('parent sha may not be none')
                # FIXME: bodge
                self.parent_sha = hashlib.sha1('parent: %s' % self.timestamp.isoformat()).hexdigest()
            elif Action.objects.filter(stream_id=self.stream_id, self_sha=self.parent_sha).count() != 1:
                raise Exception('parent not found: %r' % self.parent_sha)

        hash_base = [
            self.timestamp.isoformat(),
            self.parent_sha,
            self.author.name,
            self.message
        ]
        self.self_sha = hashlib.sha1('\n'.join(hash_base)).hexdigest()
        print 'saving', self
        return super(Action, self).save(**kwargs)

    def __unicode__(self):
        return self.message[:50]

    class Meta:
        ordering = ['id']
