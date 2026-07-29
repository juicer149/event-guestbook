from django.test import TestCase

from guestbook.models import Post, PostImage


class PostModelTests(TestCase):
    def test_posts_are_ordered_newest_first(self) -> None:
        older = Post.objects.create()
        newer = Post.objects.create()

        self.assertEqual(
            list(Post.objects.all()),
            [
                newer,
                older,
            ],
        )

    def test_deleting_post_deletes_image_rows(self) -> None:
        post = Post.objects.create()

        PostImage.objects.create(
            post=post,
            image="guestbook/test.jpg",
            position=0,
        )

        post.delete()

        self.assertFalse(
            PostImage.objects.exists(),
        )

    def test_images_are_ordered_by_position(self) -> None:
        post = Post.objects.create()

        second = PostImage.objects.create(
            post=post,
            image="guestbook/second.jpg",
            position=1,
        )

        first = PostImage.objects.create(
            post=post,
            image="guestbook/first.jpg",
            position=0,
        )

        self.assertEqual(
            list(post.images.all()),
            [
                first,
                second,
            ],
        )
