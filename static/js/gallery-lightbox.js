(function () {
    const lightbox = document.querySelector(
        "[data-gallery-lightbox]"
    );

    if (!lightbox) {
        return;
    }

    const image = lightbox.querySelector(
        ".gallery-lightbox__image"
    );
    const caption = lightbox.querySelector(
        "[data-gallery-caption]"
    );
    const count = lightbox.querySelector(
        "[data-gallery-count]"
    );
    const downloadLink = lightbox.querySelector(
        "[data-gallery-download]"
    );
    const closeButton = lightbox.querySelector(
        ".gallery-lightbox__close"
    );
    const previousButton = lightbox.querySelector(
        "[data-gallery-prev]"
    );
    const nextButton = lightbox.querySelector(
        "[data-gallery-next]"
    );

    let images = [];
    let currentIndex = 0;
    let previousFocus = null;
    let touchStartX = null;

    function readGallery(galleryId) {
        const gallery = document.getElementById(galleryId);

        if (!gallery) {
            return [];
        }

        return Array.from(
            gallery.querySelectorAll(
                "a[data-gallery-image]"
            )
        ).map((link) => {
            return {
                src: link.href,
                alt: link.dataset.alt || "",
                caption: link.dataset.caption || "",
                trigger: link,
            };
        });
    }

    function showImage(index) {
        if (images.length === 0) {
            return;
        }

        currentIndex = (
            index + images.length
        ) % images.length;

        const currentImage = images[currentIndex];

        image.src = currentImage.src;
        image.alt = currentImage.alt;

        caption.textContent = currentImage.caption;
        caption.hidden = !currentImage.caption;

        count.textContent = (
            `${currentIndex + 1} / ${images.length}`
        );

        downloadLink.href = currentImage.src;

        const hasMultipleImages = images.length > 1;

        previousButton.hidden = !hasMultipleImages;
        nextButton.hidden = !hasMultipleImages;
    }

    function openLightbox(trigger) {
        const galleryId = trigger.dataset.galleryId;

        images = readGallery(galleryId);

        if (images.length === 0) {
            return;
        }

        const clickedIndex = images.findIndex(
            (galleryImage) => (
                galleryImage.trigger === trigger
            )
        );

        previousFocus = trigger;

        lightbox.hidden = false;
        lightbox.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.classList.add(
            "lightbox-open"
        );

        showImage(
            clickedIndex >= 0
                ? clickedIndex
                : 0
        );

        closeButton.focus();
    }

    function closeLightbox() {
        lightbox.hidden = true;
        lightbox.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.classList.remove(
            "lightbox-open"
        );

        image.src = "";
        image.alt = "";

        caption.textContent = "";
        caption.hidden = true;

        count.textContent = "";
        downloadLink.removeAttribute("href");

        images = [];
        currentIndex = 0;
        touchStartX = null;

        if (previousFocus) {
            previousFocus.focus();
        }

        previousFocus = null;
    }

    function showPreviousImage() {
        showImage(currentIndex - 1);
    }

    function showNextImage() {
        showImage(currentIndex + 1);
    }

    document.addEventListener(
        "click",
        function (event) {
            const trigger = event.target.closest(
                "[data-gallery-trigger]"
            );

            if (trigger) {
                event.preventDefault();
                openLightbox(trigger);
                return;
            }

            if (
                event.target.closest(
                    "[data-gallery-close]"
                )
            ) {
                closeLightbox();
                return;
            }

            if (
                event.target.closest(
                    "[data-gallery-prev]"
                )
            ) {
                showPreviousImage();
                return;
            }

            if (
                event.target.closest(
                    "[data-gallery-next]"
                )
            ) {
                showNextImage();
            }
        }
    );

    document.addEventListener(
        "keydown",
        function (event) {
            if (lightbox.hidden) {
                return;
            }

            if (event.key === "Escape") {
                closeLightbox();
                return;
            }

            if (event.key === "ArrowLeft") {
                showPreviousImage();
                return;
            }

            if (event.key === "ArrowRight") {
                showNextImage();
            }
        }
    );

    lightbox.addEventListener(
        "touchstart",
        function (event) {
            if (event.touches.length !== 1) {
                return;
            }

            touchStartX = event.touches[0].clientX;
        },
        {
            passive: true,
        }
    );

    lightbox.addEventListener(
        "touchend",
        function (event) {
            if (
                touchStartX === null ||
                event.changedTouches.length !== 1
            ) {
                return;
            }

            const touchEndX =
                event.changedTouches[0].clientX;

            const distance = touchEndX - touchStartX;

            touchStartX = null;

            if (Math.abs(distance) < 50) {
                return;
            }

            if (distance > 0) {
                showPreviousImage();
                return;
            }

            showNextImage();
        },
        {
            passive: true,
        }
    );
})();
