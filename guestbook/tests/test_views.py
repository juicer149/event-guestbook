import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.test import TestCase, override_settings
from django.urls import reverse

from guestbook.access import (
    SESSION_GUEST_ACCESS_KEY,
)
from guestbook.lifecycle import GuestbookState
from guestbook.models import Post, PostImage
from guestbook.phase_configuration import (
    configuration_for,
)
from guestbook.phases import GuestbookPhase


TEST_MEDIA_ROOT = Path(
    tempfile.mkdtemp(
        prefix="guestbook-tests-",
    )
)

def state_for(
    phase: GuestbookPhase,
) -> GuestbookState:
    """
    Build a consistent state for view tests.

    The tests reuse the application's real phase lookup while
    replacing only the current-time resolution.
    """
    return GuestbookState(
        phase=phase,
        configuration=configuration_for(
            phase,
        ),
    )


def valid_image(
    *,
    name: str = "photo.gif",
) -> SimpleUploadedFile:
    """
    Return a minimal valid one-pixel GIF upload.
    """
    gif_bytes = (
        b"GIF89a"
        b"\x01\x00"
        b"\x01\x00"
        b"\x80"
        b"\x00"
        b"\x00"
        b"\x00\x00\x00"
        b"\xff\xff\xff"
        b"!"
        b"\xf9"
        b"\x04"
        b"\x01"
        b"\x00\x00"
        b"\x00"
        b"\x00"
        b","
        b"\x00\x00"
        b"\x00\x00"
        b"\x01\x00"
        b"\x01\x00"
        b"\x00"
        b"\x02"
        b"\x02"
        b"D\x01"
        b"\x00"
        b";"
    )

    return SimpleUploadedFile(
        name=name,
        content=gif_bytes,
        content_type="image/gif",
    )


@override_settings(
    GUESTBOOK_ACCESS_KEY="test-secret-key",
    GUESTBOOK_TITLE="Testfest",
    GUESTBOOK_MAX_IMAGES_PER_POST=20,
    GUESTBOOK_MAX_IMAGE_BYTES=(
        15 * 1024 * 1024
    ),
)
class GuestbookViewTests(TestCase):
    def join_url(
        self,
        key: str = "test-secret-key",
    ) -> str:
        return reverse(
            "guestbook:join",
            kwargs={
                "access_key": key,
            },
        )

    def index_url(self) -> str:
        return reverse(
            "guestbook:index",
        )

    def upload_url(self) -> str:
        return reverse(
            "guestbook:upload_photos",
        )

    def grant_session_access(self) -> None:
        session = self.client.session

        session[
            SESSION_GUEST_ACCESS_KEY
        ] = True

        session.save()

    def test_closed_join_returns_404(self) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.CLOSED,
            ),
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_valid_join_key_grants_access(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertRedirects(
            response,
            self.index_url(),
            fetch_redirect_response=False,
        )

        self.assertIs(
            self.client.session[
                SESSION_GUEST_ACCESS_KEY
            ],
            True,
        )

    def test_invalid_join_key_returns_404(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.join_url("wrong-key"),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    @override_settings(
        GUESTBOOK_ACCESS_KEY="",
    )
    def test_missing_configured_key_returns_404(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_join_is_allowed_in_pre(self) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.PRE,
            ),
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_join_is_allowed_in_archived(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.ARCHIVED,
            ),
        ):
            response = self.client.get(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_index_requires_guest_access(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.index_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_closed_index_returns_404_even_with_access(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.CLOSED,
            ),
        ):
            response = self.client.get(
                self.index_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_guest_can_view_pre_page(self) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.PRE,
            ),
        ):
            response = self.client.get(
                self.index_url(),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["posts"]),
            [],
        )

        self.assertFalse(
            response.context[
                "configuration"
            ].show_feed,
        )

    def test_live_page_contains_posts(self) -> None:
        self.grant_session_access()

        post = Post.objects.create()

        PostImage.objects.create(
            post=post,
            image="guestbook/test-live.jpg",
            position=0,
        )

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.index_url(),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["posts"]),
            [post],
        )

        self.assertTrue(
            response.context[
                "configuration"
            ].show_feed,
        )

    def test_archived_page_contains_posts(
        self,
    ) -> None:
        self.grant_session_access()

        post = Post.objects.create()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.ARCHIVED,
            ),
        ):
            response = self.client.get(
                self.index_url(),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["posts"]),
            [post],
        )

        self.assertFalse(
            response.context[
                "configuration"
            ].allow_uploads,
        )

    def test_upload_requires_guest_access(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_upload_is_disabled_in_pre(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.PRE,
            ),
        ):
            response = self.client.get(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_upload_is_enabled_in_live(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.get(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.context[
                "configuration"
            ].allow_camera_capture,
        )

    def test_upload_is_enabled_in_post(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.POST,
            ),
        ):
            response = self.client.get(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context[
                "configuration"
            ].allow_camera_capture,
        )

    def test_upload_is_disabled_in_archived(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.ARCHIVED,
            ),
        ):
            response = self.client.get(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_valid_upload_creates_post_and_image(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.post(
                self.upload_url(),
                {
                    "images": valid_image(),
                },
            )

        self.assertRedirects(
            response,
            self.index_url(),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            Post.objects.count(),
            1,
        )

        self.assertEqual(
            PostImage.objects.count(),
            1,
        )

        image = PostImage.objects.get()

        self.assertEqual(
            image.position,
            0,
        )

    def test_multiple_images_preserve_order(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.post(
                self.upload_url(),
                {
                    "images": [
                        valid_image(
                            name="first.gif",
                        ),
                        valid_image(
                            name="second.gif",
                        ),
                    ],
                },
            )

        self.assertEqual(
            response.status_code,
            302,
        )

        images = list(
            PostImage.objects.order_by(
                "position",
            )
        )

        self.assertEqual(
            len(images),
            2,
        )

        self.assertEqual(
            [
                image.position
                for image in images
            ],
            [
                0,
                1,
            ],
        )

    def test_invalid_upload_does_not_create_post(
        self,
    ) -> None:
        self.grant_session_access()

        invalid_file = SimpleUploadedFile(
            name="not-an-image.txt",
            content=b"not an image",
            content_type="text/plain",
        )

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.post(
                self.upload_url(),
                {
                    "images": invalid_file,
                },
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Post.objects.count(),
            0,
        )

        self.assertEqual(
            PostImage.objects.count(),
            0,
        )

        self.assertTrue(
            response.context["form"].errors,
        )

    def test_upload_endpoint_rejects_put(
        self,
    ) -> None:
        self.grant_session_access()

        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.put(
                self.upload_url(),
            )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_join_endpoint_rejects_post(
        self,
    ) -> None:
        with patch(
            "guestbook.views.current_guestbook_state",
            return_value=state_for(
                GuestbookPhase.LIVE,
            ),
        ):
            response = self.client.post(
                self.join_url(),
            )

        self.assertEqual(
            response.status_code,
            405,
        )
