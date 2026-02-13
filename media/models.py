from django.db import models
from django.utils import timezone


def upload_to_path(instance, filename):
    """Generate upload path for media files"""
    date_str = timezone.now().strftime('%Y/%m/%d')
    return f'media_uploads/{date_str}/{filename}'


class Media(models.Model):
    """Model for storing uploaded media files"""
    
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    file = models.FileField(upload_to=upload_to_path)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        default='image'
    )
    uploaded_by = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveBigIntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Media'
        verbose_name_plural = 'Media Files'
    
    def __str__(self):
        return self.title or self.file.name
    
    def save(self, *args, **kwargs):
        """Override save to set file size and content type"""
        if self.file:
            self.file_size = self.file.size
            self.content_type = self.file.content_type
        super().save(*args, **kwargs)
