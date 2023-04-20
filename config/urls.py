from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


from project_management.errors.views import handler404, handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('project_management.users.urls')),
    path('projects/', include('project_management.projects.urls')),
    path('teams/', include('project_management.teams.urls')),
    path('tasks/', include('project_management.tasks.urls')),
    path('budgets/', include('project_management.budgets.urls')),
    path('', include('project_management.home.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
