from django.db import models
from django.db.models.query import F, Q
from django.utils import timezone


from django.conf import settings 

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RandomModel(BaseModel):
    """
    This is an example model, to be used as reference in the Styleguide,
    when discussing model validation via constraints.
    """
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date",
                check=Q(start_date__lt=F("end_date"))
            )
        ]

User = settings.AUTH_USER_MODEL
class MixinFaceCheck(BaseModel):
    """
    This class that mixin model class for indicate 
    the addition property and information from actions from 
    a concrated models 
    """
    request_json = models.JSONField(null=True)
    jwt_user = models.ForeignKey(User , null=True , on_delete=models.CASCADE)
    
    class Meta:
        abstract = True 

    def __str__(self):
        return str(self.name_mixin)
    

    