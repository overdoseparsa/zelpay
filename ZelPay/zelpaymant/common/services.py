from typing import List, Dict, Any, Tuple

from zelpaymant.common.types import DjangoModelType


def model_update(
    *,
    instance: DjangoModelType,
    fields: List[str],
    data: Dict[str, Any]
) -> Tuple[DjangoModelType, bool]:
    """
    Generic update service meant to be reused in local update services

    For example:

    def user_update(*, user: User, data) -> User:
        fields = ['first_name', 'last_name']
        user, has_updated = model_update(instance=user, fields=fields, data=data)

        // Do other actions with the user here

        return user

    Return value: Tuple with the following elements:
        1. The instance we updated
        2. A boolean value representing whether we performed an update or not.
    """
    has_updated = False

    for field in fields:
        # Skip if a field is not present in the actual data
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    # Perform an update only if any of the fields was actually changed
    if has_updated:
        instance.full_clean()
        # Update only the fields that are meant to be updated.
        # Django docs reference:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        instance.save(update_fields=fields)

    return instance, has_updated


from rest_framework import mixins, serializers
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response
from abc import ABC


class MixinSerializerController(
    ABC,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericAPIView,
    ViewSetMixin,   
):

    output_serializer = None   
    serializer_class = None    
    actions = {}               

    """
    why should be like there 
    imagin you have viewset is can  mainater a nother opreation api Action 
    to controll 
    
    
    >>> class YourViewSet(MixinSerializerController):
    ... action = {
        'GET':lambda x : Response({"status":"ok"})
        }
        # and all logic is work
    ... def post(self , request, *args, **kwargs):
            return super().post(request, *args ,**kwargs)
    
    you can  inject and specify your logic if u want 
    """
    def validate_serializer(self, serializer):
        if not issubclass(serializer, serializers.Serializer):
            raise AssertionError("Bad serializer selected")

    def get_serializer_class(self):
        if self.request.method == "GET" and self.output_serializer:
            self.validate_serializer(self.output_serializer)
            return self.output_serializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        if self.actions.get("list"):
            return self.actions["list"](request, *args, **kwargs)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if self.actions.get("retrieve"):
            return self.actions["retrieve"](request, *args, **kwargs)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if self.actions.get("create"):
            return self.actions["create"](request, *args, **kwargs)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.actions.get("update"):
            return self.actions["update"](request, *args, **kwargs)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if self.actions.get("partial_update"):
            return self.actions["partial_update"](request, *args, **kwargs)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.actions.get("destroy"):
            return self.actions["destroy"](request, *args, **kwargs)
        return super().destroy(request, *args, **kwargs)
    