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
    const loader = lightbox.querySelector(
        "[data-gallery-loader]"
    );
    const errorMessage = lightbox.querySelector(
        "[data-gallery-error]"
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
    let requestedSource = "";

    const preloadedSources = new Set();

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

    function showLoadingState() {
        loader.hidden = false;
        errorMessage.hidden = true;

        image.classList.add("is-loading");

        lightbox.setAttribute(
            "aria-busy",
            "true"
        );
    }

    function showLoadedState() {
        loader.hidden = true;
        errorMessage.hidden = true;

        image.classList.remove("is-loading");

        lightbox.setAttribute(
            "aria-busy",
            "false"
        );
    }

    function showErrorState() {
        loader.hidden = true;
        errorMessage.hidden = false;

        image.classList.add("is-loading");

        lightbox.setAttribute(
            "aria-busy",
            "false"
        );
    }

    function preloadImage(source) {
        if (
            !source ||
            preloadedSources.has(source)
        ) {
            return;
        }

        preloadedSources.add(source);

        const preload = new Image();

        preload.src = source;
    }

    function preloadAdjacentImages() {
        if (images.length < 2) {
            return;
        }

        const previousIndex = (
            currentIndex - 1 + images.length
        ) % images.length;

        const nextIndex = (
            currentIndex + 1
        ) % images.length;

        preloadImage(
            images[previousIndex].src
        );

        preloadImage(
            images[nextIndex].src
        );
    }

    function showImage(index) {
        if (images.length === 0) {
            return;
        }

        currentIndex = (
            index + images.length
        ) % images.length;

        const currentImage = images[currentIndex];

        requestedSource = currentImage.src;

        showLoadingState();

        image.alt = currentImage.alt;
        image.src = currentImage.src;

        caption.textContent = currentImage.caption;
        caption.hidden = !currentImage.caption;

        count.textContent = (
            `${currentIndex + 1} / ${images.length}`
        );

        downloadLink.href = currentImage.src;

        const hasMultipleImages = images.length > 1;

        previousButton.hidden = !hasMultipleImages;
        nextButton.hidden = !hasMultipleImages;

        /*
         * A cached image may already be complete when src is assigned.
         * The naturalWidth check distinguishes a successfully decoded
         * image from a failed request.
         */
        if (
            image.complete &&
            image.naturalWidth > 0
        ) {
            showLoadedState();
            preloadAdjacentImages();
        }
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
        lightbox.setAttribute(
            "aria-busy",
            "false"
        );

        document.body.classList.remove(
            "lightbox-open"
        );

        requestedSource = "";

        image.removeAttribute("src");
        image.alt = "";
        image.classList.remove("is-loading");

        loader.hidden = true;
        errorMessage.hidden = true;

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

    image.addEventListener(
        "load",
        function () {
            if (image.src !== requestedSource) {
                return;
            }

            showLoadedState();
            preloadAdjacentImages();
        }
    );

    image.addEventListener(
        "error",
        function () {
            if (image.src !== requestedSource) {
                return;
            }

            showErrorState();
        }
    );

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
