from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate


class ResultsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.object = None
        self.url = ""
        self.viewset = None

    def _test_access(self, user):
        request = self.factory.get(self.url + "1/")
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"get": "retrieve"})
        return view(request, pk=self.object.pk)

    def _test_list(self, user):
        request = self.factory.get(self.url)
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"get": "list"})
        return view(request)

    def _test_create(self, user, data):
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"post": "create"})
        return view(request)

    def _test_delete(self, user):
        request = self.factory.delete(self.url + "1/")
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"delete": "destroy"})
        return view(request, pk=1)

    def _test_update(self, user, data):
        request = self.factory.put(self.url + "1/", data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"put": "update"})
        return view(request, pk=1)

    def _test_patch(self, user, data):
        request = self.factory.patch(self.url + "1/", data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"patch": "partial_update"})
        return view(request, pk=1)
