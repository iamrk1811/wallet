from django.urls import include, re_path

from rest_framework.routers import DefaultRouter


class JuloWalletRouer(DefaultRouter):
    def __init__(self, *args, **kwargs):
        self._extended_routers = []
        return super(JuloWalletRouer, self).__init__(*args, **kwargs)

    def extend(self, url_prefix, router):
        """Allows to include additional URLs to the router
        `router` can be any object (e.g. Router or App) which supports a `.urls` property
        """
        self._extended_routers.append((url_prefix, router))

    def get_urls(self):
        urls = super(JuloWalletRouer, self).get_urls()

        # Add the extended router
        urls.extend([self.get_router_url(prefix, router) for prefix, router in self._extended_routers])
        return urls

    def get_router_url(self, prefix, router):
        if isinstance(router, tuple):
            # This means that the argument is a url pattern
            return re_path(r'%s/' % prefix, router)

        # Else, assume that it is a router and it supports a `urls` paramter
        return re_path(r'%s/' % prefix, include(router.urls))