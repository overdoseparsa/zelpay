import logging
from django.db import models
from django.http import HttpRequest
from abc import ABC, abstractmethod

from .provider import (
    send_request_zarinpall,
    verify_request_zarinpall,
)
from zelpaymant.paymant.models import Transactions

logger = logging.getLogger(__name__) # TODO add log from django

class GatewayMixin:
    """Base mixin for saving gateway configuration."""

    def save(self, *args, **kwargs):
        raise NotImplementedError("Must be implemented in subclass")


class DjangoGatewayMixin(GatewayMixin):
    model = Transactions

    @property
    def get_model(self) -> models.Model:
        assert issubclass(self.model, models.Model)
        return self.model

    def save(self, *args, **kwargs):
        user = kwargs.get("user") or (args[0] if isinstance(args[0], self.model) else None)
        assert user, "No authenticated user provided"

        transaction_payload = kwargs.get("transaction")
        request: HttpRequest = kwargs["request"]

        instance = self.get_model(
            user=user,
            transaction_data=transaction_payload,
            token=kwargs.get("token", "N/A"),
            request_payload={
                "header": dict(request.headers),
                "body": dict(request.GET) if request.GET else dict(request.POST),
                "meta": dict(request.META),
                "tls": request.is_secure(),
            },
            authority=kwargs["authority"],
        )
        instance.save()

        logger.info(
            f"Transaction saved | user={user.id} authority={kwargs['authority']} "
            f"token={instance.token}"
        )
        return instance


class AbstractGateway(ABC, GatewayMixin):
    """Abstract base class for all payment gateways."""

    meta_gateway = {}

    @classmethod
    def get_metadata(cls):
        return cls.meta_gateway

    @abstractmethod
    def request_gateway(self, *args, **kwargs):
        pass

    @abstractmethod
    def verify_gateway(self, *args, **kwargs):
        pass

    def __init__(self, **data):
        self.data = data

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __call__(self):
        return f"Sending payment with {self.data}"

    def __repr__(self):
        return f"<Gateway {self.__class__.__name__}: {self.data}>"


class ZarinGateway(AbstractGateway, DjangoGatewayMixin):
    """Zarinpal payment gateway implementation."""

    meta_gateway = {
        "currency": "IRT",
        "callback_url": "http://your-site.com/verify",
        "merchant": "",  # TODO: load from settings
        "metadata": {
            "email": "parsakhakiy@gmail.com",
            "mobile": "09932667257",
        },
    }

    ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
    ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

    def __init__(self, **kwargs):
        meta = self.get_metadata()
        meta.update(kwargs)
        self.transaction_data = meta
        self.request = kwargs.get("request")
        self.response = None
        assert self.transaction_data.get('merchant') and self.transaction_data.get("description")
 
    def request_gateway(self, **kwargs):
        logger.debug(f"Requesting Zarinpal gateway with payload={self.transaction_data}")
        try:
            self.response = send_request_zarinpall(
            **self.transaction_data
            )
            logger.info(f"Zarinpal request successful | response={self.response}")
            return self.log_after_request()
        except Exception as e:
            logger.error(f"Zarinpal request failed | error={e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def verify_gateway(self, **kwargs):
        logger.debug(f"Verifying transaction with payload={kwargs}")
        try:
            response = verify_request_zarinpall(
                self.ZP_API_VERIFY,
                  kwargs
                )
            logger.info(f"Verification successful | response={response}")
            return response
        except Exception as e:
            logger.error(f"Verification failed | error={e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def log_after_request(self):
        logger.debug("Saving transaction after request...")
        return self.save(
            user=self.request.user,
            request=self.request,
            transaction=self.transaction_data,
            authority=self.response["data"]["authority"],
            token=self.response["data"]["authority"],
        )
