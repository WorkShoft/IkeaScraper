from django.db import models


class Color(models.Model):
    product_id = models.TextField()
    url = models.TextField()
    color_name = models.TextField()
    color_id = models.TextField()

    def __str__(self):
        return self.color_name

    def as_dict(self):
        return {
            "productId": self.product_id,
            "url": self.url,
            "colorName": self.color_name,
            "colorId": self.color_id,
        }

    
class SofaType(models.Model):
    description = models.TextField(unique=True)

    def __str__(self):
        return self.description

    
class Sofa(models.Model):
    name = models.TextField()
    image_url = models.TextField()
    type = models.ForeignKey(SofaType, on_delete=models.CASCADE)
    colors = models.ManyToManyField(Color, related_name="colors")

    def __str__(self):
        return f"{self.name} {self.type}"

    def as_dict(self):
        return {
            "name": self.name,
            "type": str(self.type),
            "imageUrl": self.image_url,
            "colors": [c.as_dict() for c in self.colors.all()]
        }


