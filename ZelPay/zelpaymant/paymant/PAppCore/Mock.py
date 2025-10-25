from .gateway import * 

logger = Logger(__name__)
import uuid
import psycopg2
"""
INSERT INTO Transactions (metadata, uuid_field)
VALUES ('تراکنش تستی', gen_random_uuid());

"""
def insert_user(meta ,uuid):
    try:
        # اتصال به دیتابیس
        conn = psycopg2.connect(
            dbname='zelpaymant',
            user='ZELLIT',
            password='mohamadkhaki83@',
            host='0.0.0.0',
            port=5432
        )
        cur = conn.cursor()

        # اجرای کوئری INSERT
        cur.execute(
            "INSERT INTO Transactions (metadata, uuid_field) VALUES (%s, %s)",
            (meta, uuid)
        )

        conn.commit()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

class MockTransactionMixin(TransactionMixin):
    def save_transaction(self, response):
        
        insert_user(
            meta = response['Mdata'] , uuid = response['uuid']
        )
        # get from redis it is better 

class MockGatewayRequest(BasePaymentGateway):
    def send_request(self, callback_url = 'http://CallBackurl.com'):
        def mock_send_request(**Kwargs):
            print('requesting from mock data is ' , Kwargs)
            return {
                'uuid':uuid.uuid4(),
                'Mdata':str(Kwargs)
                  # for exsamle  
            }
        super().send_request(callback_url)
    
        logger.info(
            f"The send_request Data is \'{self._data}\'"
        )
        response = self
        self.save_transaction(response)
        # save from Cache 
        # insert from database 
        # return UUID FOR Check 

class MockGatwayverifiction():
    pass