(() => {
    let previouslyFocused = null;

    function closeReview(overlay) {
        if (!overlay) return;
        overlay.hidden = true;
        document.body.style.overflow = '';
        if (previouslyFocused) previouslyFocused.focus();
    }

    document.addEventListener('click', (event) => {
        const openButton = event.target.closest('[data-rule-review-open]');
        if (openButton) {
            const overlay = document.getElementById(openButton.dataset.ruleReviewOpen);
            if (!overlay) return;
            previouslyFocused = openButton;
            overlay.hidden = false;
            document.body.style.overflow = 'hidden';
            overlay.querySelector('[data-rule-review-close]')?.focus();
            return;
        }

        const closeButton = event.target.closest('[data-rule-review-close]');
        if (closeButton) {
            closeReview(closeButton.closest('[data-rule-review-overlay]'));
            return;
        }

        if (event.target.matches('[data-rule-review-overlay]')) {
            closeReview(event.target);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const openOverlay = document.querySelector('[data-rule-review-overlay]:not([hidden])');
        closeReview(openOverlay);
    });
})();
