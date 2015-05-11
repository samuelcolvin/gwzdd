from django.contrib import messages
from django.db import transaction
from django.views.generic import TemplateView, DetailView
from .models import Stream


class IndexView(TemplateView):
    template_name = 'index.jinja'

    def get_context_data(self, **kwargs):
        with transaction.atomic():
            if not Stream.objects.all().exists():
                messages.info(self.request, 'No stream exist, creating one')
                Stream.objects.create(name='base stream')

        return super(IndexView, self).get_context_data(
            streams=Stream.objects.all(),
            **kwargs
        )

index_view = IndexView.as_view()


class LowLevelView(TemplateView):
    template_name = 'low_level.jinja'

    def get_context_data(self, **kwargs):
        return super(LowLevelView, self).get_context_data(
            ws_url='ws://localhost:8001/',
            **kwargs
        )

low_level_view = LowLevelView.as_view()


class StreamView(DetailView):
    template_name = 'stream.jinja'
    model = Stream

    def get_context_data(self, **kwargs):
        return super(StreamView, self).get_context_data(
            ws_url='ws://localhost:8001/',
            **kwargs
        )

stream_view = StreamView.as_view()
