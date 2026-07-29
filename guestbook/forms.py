from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


DEFAULT_MAX_IMAGES = 20
DEFAULT_MAX_IMAGE_BYTES = 15 * 1024 * 1024


class MultipleImageInput(forms.ClearableFileInput):
    """
    Allow the browser to select multiple files for one form field.
    """

    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """
    Validate every uploaded file as a Django ImageField.

    Django normally validates one file per ImageField. This field
    applies the same validation separately to every selected file.
    """

    widget = MultipleImageInput

    def clean(
        self,
        data: Any,
        initial: Any = None,
    ) -> list[UploadedFile]:
        clean_single_image = super().clean

        if not data:
            if self.required:
                raise ValidationError(
                    self.error_messages["required"],
                    code="required",
                )

            return []

        if isinstance(data, (list, tuple)):
            return [
                clean_single_image(image, initial)
                for image in data
            ]

        return [
            clean_single_image(data, initial),
        ]


class PostUploadForm(forms.Form):
    """
    Validate one photo upload action.

    Phase-dependent rules are passed into the form by the view.
    The form does not determine the current phase itself.
    """

    images = MultipleImageField(
        label="Bilder",
        required=True,
        widget=MultipleImageInput(
            attrs={
                "accept": "image/*",
            },
        ),
    )

    def __init__(
        self,
        *args: Any,
        allow_multiple_images: bool = True,
        max_images: int = DEFAULT_MAX_IMAGES,
        max_image_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if max_images < 1:
            raise ValueError(
                "max_images must be at least 1."
            )

        if max_image_bytes < 1:
            raise ValueError(
                "max_image_bytes must be at least 1."
            )

        self.allow_multiple_images = allow_multiple_images
        self.max_images = max_images
        self.max_image_bytes = max_image_bytes

    def clean_images(
        self,
    ) -> list[UploadedFile]:
        images = self.cleaned_data["images"]

        if (
            not self.allow_multiple_images
            and len(images) > 1
        ):
            raise ValidationError(
                "Du kan bara ladda upp en bild åt gången."
            )

        if len(images) > self.max_images:
            raise ValidationError(
                (
                    "Du kan som mest ladda upp "
                    f"{self.max_images} bilder åt gången."
                )
            )

        oversized_images = [
            image.name
            for image in images
            if image.size > self.max_image_bytes
        ]

        if oversized_images:
            max_megabytes = (
                self.max_image_bytes
                // (1024 * 1024)
            )

            raise ValidationError(
                (
                    "Varje bild får vara högst "
                    f"{max_megabytes} MB."
                )
            )

        return images
