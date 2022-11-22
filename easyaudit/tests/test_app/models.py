import uuid

from django.db import models


class TestModel(models.Model):
    name = models.CharField(max_length=50, default='test data')


class TestForeignKey(models.Model):
    name = models.CharField(max_length=50)
    test_fk = models.ForeignKey(TestModel, on_delete=models.CASCADE)


class TestM2M(models.Model):
    name = models.CharField(max_length=50)
    test_m2m = models.ManyToManyField(TestModel)


class TestUUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=50, default='test data')


class TestUUIDForeignKey(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=50)
    test_fk = models.ForeignKey(TestUUIDModel, on_delete=models.CASCADE)


class TestUUIDM2M(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(max_length=50)
    test_m2m = models.ManyToManyField(TestUUIDModel)


class TestBigIntModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default='test data')


class TestBigIntForeignKey(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    test_fk = models.ForeignKey(TestBigIntModel, on_delete=models.CASCADE)


class TestBigIntM2M(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    test_m2m = models.ManyToManyField(TestBigIntModel)


class TestMetadataAModel(models.Model):
    name = models.CharField(max_length=50, default="metadata A")


class TestMetadataBModel(models.Model):
    name = models.CharField(max_length=50, default="metadata B")

    model_a = models.ForeignKey(TestMetadataAModel, on_delete=models.CASCADE)

    def get_easyaudit_metadata(self):
        return dict(model_a_id=self.model_a_id)


class TestMetadataCModel(models.Model):
    EASY_AUDIT_METADATA_METHOD = "fetch_metadata"

    name = models.CharField(max_length=50, default="metadata C")

    model_b = models.ForeignKey(TestMetadataBModel, on_delete=models.CASCADE)

    def fetch_metadata(self):
        return dict(model_a_id=self.model_b.model_a_id, model_b_id=self.model_b.id)
