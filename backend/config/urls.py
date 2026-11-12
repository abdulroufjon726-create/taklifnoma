from pathlib import Path

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve as static_serve

DIST_DIR = settings.BASE_DIR.parent / "frontend" / "dist"


def spa_index(request, route=""):
    """
    Serve the built Vue app (or a hint page while developing).
    During development the Vite dev server (http://localhost:5173) is used
    and this view is never reached.
    """
    index = DIST_DIR / "index.html"
    if index.exists():
        return HttpResponse(
            index.read_text(encoding="utf-8"),
            content_type="text/html; charset=utf-8",
        )
    return HttpResponse(
        "<!doctype html><html lang='uz'><head><meta charset='utf-8'>"
        "<title>Taklifnoma</title><style>body{font-family:system-ui;display:grid;"
        "place-items:center;height:100vh;margin:0;background:#0b0a12;color:#eee}"
        ".c{text-align:center;max-width:520px;padding:24px}code{background:#1e1b2e;"
        "padding:3px 8px;border-radius:8px}</style></head><body><div class='c'>"
        "<h1>Taklifnoma</h1><p>Frontend hali build qilinmagan.</p>"
        "<p>Development rejimda:</p><p><code>cd frontend &amp;&amp; npm run dev</code> "
        "&rarr; <a style='color:#8b7cf6' href='http://localhost:5173'>http://localhost:5173</a></p>"
        "<p>Yoki production uchun: <code>cd frontend &amp;&amp; npm run build</code></p>"
        "</div></body></html>",
        content_type="text/html; charset=utf-8",
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("invitations.urls")),
]

# Static assets of the built frontend
if (DIST_DIR / "assets").is_dir():
    urlpatterns += [
        re_path(
            r"^assets/(?P<path>.*)$",
            static_serve,
            {"document_root": DIST_DIR / "assets"},
        ),
    ]

# SPA catch-all (must be last)
urlpatterns += [
    re_path(r"^(?!api/|admin/|static/).*$", spa_index),
]
