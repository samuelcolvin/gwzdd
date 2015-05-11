from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'base.jinja'

    def get_context_data(self):
        ws_url = 'ws://localhost:8001/'
        return super(MainView, self).get_context_data(
            ws_url=ws_url
        )

main_view = MainView.as_view()
