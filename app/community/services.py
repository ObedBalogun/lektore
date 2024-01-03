from rest_framework.pagination import PageNumberPagination

from app.community.models import CommunityPost, PostAppraisal
from app.community.serializers import CommunityPostSerializer


class CommunityService:
    @classmethod
    def create_post(cls, request, **kwargs):
        post_owner = request.user
        post = CommunityPost(post_owner=post_owner, **kwargs)
        post.save()
        response = {key: post.__dict__[key] for key in post.__dict__.keys() if key[0] != "_"}

        return dict(data=response,
                    message="Post created Successfully!")

    @classmethod
    def appraise_post(cls, request, **kwargs):
        appraised_by = request.user
        post_id = kwargs.pop('post_id')
        appraisal_type = kwargs.pop('appraisal_type')
        try:
            post = CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return dict(error="Post not found")

        PostAppraisal.objects.create(post=post, appraisal_type=appraisal_type, appraised_by=appraised_by)
        response = {
            "likes": post.likes,
            "loves": post.loves
        }
        return dict(
            data=response,
            message=f"post {appraisal_type}d successfully!")

    @classmethod
    def remove_appraisal(cls, request, **kwargs):
        appraised_by = request.user
        post_id = kwargs.pop('post_id')
        try:
            post = CommunityPost.objects.get(id=post_id)
            appraisal = PostAppraisal.objects.get(post=post, appraised_by=appraised_by)
            appraisal.delete()
        except CommunityPost.DoesNotExist:
            return dict(error="Post not found")
        except PostAppraisal.DoesNotExist:
            pass

        return dict(message="Appraisal successfully removed!")

    @staticmethod
    def add_extra_attributes(list_of_dicts):
        for d in list_of_dicts:
            post = CommunityPost.objects.get(id=d.get('id'))
            extra_attributes = {"likes": post.likes, "loves": post.loves}
            d.update(extra_attributes)

    @classmethod
    def get_community_posts(cls, request, order=None,):
        community_posts = CommunityPost.objects.all()
        if order == "latest":
            community_posts = community_posts.order_by('-created')
        else:
            community_posts = community_posts.order_by('created')
        serialized_data = CommunityPostSerializer(community_posts, many=True)
        paginator_instance = PageNumberPagination()
        queryset = serialized_data.data
        paginator_instance.page_size = 2
        paginated_result = paginator_instance.paginate_queryset(queryset, request)
        cls.add_extra_attributes(paginated_result)

        return dict(data=paginated_result)
