from django.db import models

# Create your models here
import secrets
from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paystack_access_code = models.CharField(max_length=100, blank=True)
    paystack_transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def generate_reference(self):
        while True:
            reference = f"paystack_{secrets.token_urlsafe(16)}"
            if not Payment.objects.filter(reference=reference).exists():
                return reference

    def __str__(self):
        return f"{self.reference} - {self.amount}"

    class Meta:
        ordering = ['-created_at']
