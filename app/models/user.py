import random
import string

from app.database import Base

from itsdangerous import (TimedJSONWebSignatureSerializer as
                          Serializer,
                          BadSignature,
                          SignatureExpired)

from sqlalchemy import Column, Integer, String


secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:  # Valid Token, but expired
            return None
        except BadSignature:  # Invalid Token
            return None
        user_id = data['id']
        return user_id
