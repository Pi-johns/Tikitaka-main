from django.db import models

class Slide(models.Model):
    heading = models.CharField(max_length=100)
    subheading = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='slides/')
    
    primary_button_text = models.CharField(max_length=50, blank=True)
    primary_button_link = models.URLField(blank=True)

    secondary_button_text = models.CharField(max_length=50, blank=True)
    secondary_button_link = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.heading
