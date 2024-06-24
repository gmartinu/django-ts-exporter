from django.db import models


class RelatedModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


class TestModel(models.Model):
    char_field = models.CharField(max_length=100)
    integer_field = models.IntegerField()
    boolean_field = models.BooleanField()
    datetime_field = models.DateTimeField()
    date_field = models.DateField()
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    uuid_field = models.UUIDField()
    json_field = models.JSONField()
    foreign_key = models.ForeignKey(
        RelatedModel, on_delete=models.CASCADE, related_name="fk_related"
    )
    many_to_many = models.ManyToManyField(RelatedModel, related_name="m2m_related")
    one_to_one = models.OneToOneField(
        RelatedModel, on_delete=models.CASCADE, related_name="o2o_related"
    )
    file_field = models.FileField()

    class Meta:
        app_label = "tests"
