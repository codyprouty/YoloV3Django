from django.db import models

# Create your models here.





class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name

class Photo(models.Model):
    class Meta:
        verbose_name='Photo'
        verbose_name_plural = 'Photos'
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.description

class Config(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.description