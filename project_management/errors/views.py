from django.shortcuts import render
from django.http import Http404, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views.generic import TemplateView



def handler404(request, exception):
    return render(request, 'error/page-404.html', status=404)


def handler500(request):
    return render(request, 'error/page-500.html', status=500)


class ErrorHandlerMixin(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except (TemplateDoesNotExist, Http404):
            # Render a custom 404 error page template
            return render(request, "error/page-404.html", status=404)
        except HttpResponseForbidden:
            # Render a custom 403 error page template
            return render(request, "error/page-403.html", status=403)
        except HttpResponseServerError:
            # Render a custom 500 error page template
            return render(request, "error/page-500.html", status=500)
        except Exception as e:
            # Render a custom error page template for all other exceptions
            return render(request, "error/page-error.html", {"exception": e}, status=500)
        
        # Return the response if no exception occurred
        return response
