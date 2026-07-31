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
        )

        post.delete()

        self.assertFalse(
            PostImage.objects.exists(),
        )


class PostImageModelTests(TestCase):
    def test_images_are_ordered_newest_first(self) -> None:
        post = Post.objects.create()

        older = PostImage.objects.create(
            post=post,
            image="guestbook/older.jpg",
        )

        newer = PostImage.objects.create(
            post=post,
            image="guestbook/newer.jpg",
        )

        self.assertEqual(
            list(PostImage.objects.all()),
            [
                newer,
                older,
            ],
        )

    def test_post_groups_uploaded_images(self) -> None:
        post = Post.objects.create()

        first = PostImage.objects.create(
            post=post,
            image="guestbook/first.jpg",
        )

        second = PostImage.objects.create(
            post=post,
            image="guestbook/second.jpg",
        )

        self.assertCountEqual(
            post.images.all(),
            [
                first,
                second,
            ],
        )
