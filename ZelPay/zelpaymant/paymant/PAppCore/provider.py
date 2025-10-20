import requests 
import json 

def send_request_zarinpall(
        ZP_API_REQUEST:str=None,
        MERCHANT:str=None,
        callbackURL:str=None,
        amount:str=None,
        description:str=None,
        email=None, 
        mobile=None,
        **kwargs,
        )-> dict:

        req_data = {
            "merchant_id": MERCHANT or kwargs.get('merchant'), 
            "amount": amount or kwargs.get('amount') ,
            "callback_url": callbackURL or kwargs.get('callback_url'),
            "description": description or kwargs.get('description') ,
            "metadata": {"mobile": mobile, "email": email} or kwargs.get('metadata')
        }
        print(
            "the Request req_data is " , req_data
        )

        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        
        if len(req.json()['errors']) == 0:
            authority = req.json()['data']['authority']
            return req.json()

        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return {"message": e_message, "error_code": e_code}


def verify_request_zarinpall(
        pyload:dict, 
        MERCHANT:str,
        amount:str,
        ZP_API_VERIFY:str,
        ):
        t_status = pyload.get('Status') 
        t_authority = pyload.get('Authority') or pyload.get('Authority') 
        assert t_authority , "must be have Authority key from pyload "
        if t_status == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req_data = {
                "merchant_id": MERCHANT,
                "amount": amount,
                "authority": t_authority
            }
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_verify_status = req.json()['data']['code']
                if t_verify_status == 100:

                    return {"transaction": True, "pay": True, "RefID": req.json()['data']['ref_id'], "message": None}

                elif t_verify_status == 101:
                    return {"transaction": True, "pay": False, "RefID": None, "message": req.json()['data']['message']}
                else:
                    return {"transaction": False, "pay": False, "RefID": None, "message": req.json()['data']['message']}

            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']

                return {"status": 'ok', "message": e_message, "error_code": e_code}
        else:
            return {"status": 'cancel', "message": 'transaction failed or canceled by user'}