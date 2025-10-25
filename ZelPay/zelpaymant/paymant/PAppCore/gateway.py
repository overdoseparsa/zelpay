from abc import ABC, abstractmethod
from typing import Dict, Any , Self
from functools import cache 
# provider : save the tranamaction in columns and add to the wallet 
from logging import Logger
class TransactionMixin(ABC):
    

    def save_transaction(self, user_id: int, data: Dict[str, Any]) -> None:
        """ذخیره تاریخچه تراکنش در دیتابیس"""
        raise NotImplementedError

    def validate_transaction(self, data: Dict[str, Any]) -> bool:
        """اعتبارسنجی داده‌های تراکنش"""
        raise NotImplementedError

    def generate_token(self) -> str:
        """تولید توکن یکتا برای تراکنش"""
        raise NotImplementedError




class DjangoTransaction(TransactionMixin):# GET THE ORMS HERE 
    pass

class MockRequets():...

# --- Base Payment Gateway ---
# it is better to be in redis 
class BasePaymentGateway(ABC,TransactionMixin):=
    authorize = None

    def pass_request(self,request:Any=None):
        """
        imaggin you want to pass some speaialize data 
        from your logic 
        you logic request is difreent 
        you will pass your request to the this sections  
                
        """
        
        self._data['request'] = request 
    @staticmethod
    def static_authorize():...
        # select authorize from mytable ; 

    @classmethod
    def get_authorize(cls):
        if hasattr(cls,'authorize'):
            return cls.authorize
        elif static_authorize:=cls.static_authorize():  # it can be overloaded 
            return static_authorize
        else : 
            return None 

  
    def __init__(self, config: Dict[str, Any]): 

        self.__authorize = config.get('authorize') or self.get_authorize() 
        assert self.__authorize , "That provider Dont set authorize GatWay for ZarinPall"
        
        self.__amount = config.get('amount')
        assert (self.__amount) and (isinstance(self.__amount,str)) , "Amount not set or not Valid Values"
        
        self.__description = str(config.get('description'))
        assert self.__description , "Must set description"
        self.token_transaction = self.generate_token()

    def set_config(self,**meta): # you can overload 
        self.config = {
            'authorize':self.__authorize,
            'amount':self.__amount,
            'description':self.__description,
            **meta,
        }
        return self.config


    @abstractmethod
    def send_request(self, callback_url: str = None) -> Dict[str, Any]:
        """ارسال درخواست پرداخت به درگاه"""
        if callback_url:
            self.callback_url = callback_url
        else : 
            self.callback_url = self.prefer_callback_url # property 

        assert self.callback_url , "must set callback_url"
        self._data = self.set_config()
        self._data['callback_url'] = self.callback_url





    @abstractmethod
    @property
    def prefer_callback_url(self):
        pass # must be implement 


class BaseVerification(ABC,TransactionMixin):
    def __init__(self,token):
        super().__init__()
    @abstractmethod
    def verify_transaction(self, authority: str) -> Dict[str, Any]:
        """تأیید پرداخت بعد از بازگشت کاربر"""
        pass# --- Example: Zarinpal Gateway ---
    @abstractmethod
    def refund(self, transaction_id: str) -> Dict[str, Any]:
        """بازگشت وجه"""
        pass # remove from get status 

    @abstractmethod
    def get_status(self, transaction_id: str) -> Dict[str, Any]:
        """دریافت وضعیت تراکنش"""
        pass

from .provider import send_request_zarinpall

class ZarinpalGatewayReq(BasePaymentGateway):
    # TODO add the request mock for 
    def __init__(self, config):
        super().__init__(config)
        # more argumans
        """
        set a nother argumant to the this ZarinpalGateway 
        """
        
        self.__currency = config.get('currency')
        self.__metadata = config.get('metadata')
        

    def set_config(self, **meta):
        # TODO add log here 
        config = super().set_config(**meta)
        config['merchant_id'] = config.pop('authorize')

        if self.__currency:
            config['currency'] = self.__currency

        if self.__metadata:
            config['metadata'] = self.__metadata
        # the config we sended is from server     
        return config


    def send_request(self,callback_url: str=None) -> Dict[str, Any]:
        super().send_request(callback_url) # Set __data
        self.validate_transaction()
        # check the idempotancy 
        self
        response =  send_request_zarinpall(
            "https://payment.zarinpal.com/pg/v4/payment/request.json" ,
            **self._data
        )
        self.save_transaction(response) 
         



class ZarinpalGatewayVer(BaseVerification):
    def __init__(self, token):
        super().__init__(token)

    def verify_transaction(self, authority):...
        # get from cache or database and 
        
    def validate_transaction(self, data):
        return super().validate_transaction(data) 
        # check some validations from ransactaion  
    def save_transaction_history(self, user_id, data):
        self.add_to_wallet()
        return super().save_transaction_history(user_id, data) 

    def add_to_wallet(self, user_id: int, amount: int) -> None:
        """افزودن مبلغ به کیف پول کاربر"""
        raise NotImplementedError

# --- Transaction Manager ---
class TransactionManager:
    gateways = {
        "zarinpal": ZarinpalGatewayReq,
        # "paypal": PayPalGateway,
        # "stripe": StripeGateway,
    }

    @classmethod
    def get_gateway(cls, name: str, config: Dict[str, Any]) -> BasePaymentGateway:
        gateway_class = cls.gateways.get(name)
        if not gateway_class:
            raise ValueError(f"Gateway {name} not supported")
        return gateway_class(config)


# --- Usage in API ---

'''

app('/payment')
def set_url_param(self , request):
    if request.data['paymant'] == 'zarain':
        paymant = ZarinPament(
            **requets.data['data']
        )
        paymant.send_request()
    try:
        return Response(
            'status':ok , 'auhtority':str(paymant)
        )
    except Exceptions as E ;
        return Response(
            'status':500 , 'code':"E"        
            )
    def payment_view(request):
        gateway_name = request.data.get("gateway")
        config = request.data.get("config", {})
        amount = request.data.get("amount")
        callback_url = request.data.get("callback_url")

        try:
        
            gateway = TransactionManager.get_gateway(gateway_name, config)
            result = gateway.send_request(amount, callback_url)
            return Response({"status": "ok", "data": result})


            
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

'''