import uuid

from django.contrib.auth.models import User
from django.db import models

from app.shared_models import Timestamp


class CommunityPost(Timestamp):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="community_posts")
    post_title = models.CharField(max_length=50)
    post_body = models.TextField()

    def __str__(self):
        return f"{self.post_title} by {self.post_owner}"

    @property
    def likes(self):
        return self.appraisals.filter(appraisal_type='like').count()

    @property
    def loves(self):
        return self.appraisals.filter(appraisal_type='love').count()


class PostAppraisal(Timestamp):
    APPRAISAL_CHOICES = (
        ("like", "Like"),
        ("love", "Love")
    )
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="appraisals")
    appraised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appraisals")
    appraisal_type = models.CharField(max_length=5, choices=APPRAISAL_CHOICES)

    class Meta:
        unique_together = ("post", "appraised_by")

    def __str__(self):
        return f"{self.post.id} {self.appraisal_type}d by {self.appraised_by}"
