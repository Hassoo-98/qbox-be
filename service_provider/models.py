from django.db import models
class seriveProvider(models.Model):
   serive_provier_name=models.CharField(max_length=100)
   buisness_registration_number=models.CharField(max_length=100)
   contact_person_number=models.CharField(max_length=100)
   phone_number=models.CharField(max_length=10)
   email=models.EmailField(max_length=50)
   operating_cities=models.enums(["makkah","madinah","riyadh"])
   settlement_cycle=models.IntegerField(default=0)
   markup_type=models.enums(["fixed","percentage"])
   markup_value=models.IntegerField(default=0)
   
