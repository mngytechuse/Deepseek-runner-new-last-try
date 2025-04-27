// Educational Book Generator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const bookForm = document.getElementById('bookForm');
    if (bookForm) {
        bookForm.addEventListener('submit', function(event) {
            const syllabusInput = document.getElementById('syllabus');
            const subjectInput = document.getElementById('subject');
            
            // Validate syllabus content
            if (syllabusInput.value.trim().length < 20) {
                event.preventDefault();
                alert('Please enter a more detailed syllabus content (at least 20 characters).');
                syllabusInput.focus();
                return false;
            }
            
            // Validate subject
            if (subjectInput.value.trim().length < 3) {
                event.preventDefault();
                alert('Please enter a valid subject name (at least 3 characters).');
                subjectInput.focus();
                return false;
            }
            
            // Show loading animation or redirect to loading page
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            
            return true;
        });
    }
    
    // Handle downloads on the loading page
    const downloadDocxBtn = document.getElementById('downloadDocx');
    const downloadPdfBtn = document.getElementById('downloadPdf');
    
    if (downloadDocxBtn && downloadPdfBtn) {
        // Get the book_id from the URL
        const pathParts = window.location.pathname.split('/');
        const bookId = pathParts[pathParts.length - 1];
        
        // Set download URLs
        downloadDocxBtn.href = `/download/${bookId}/docx`;
        downloadPdfBtn.href = `/download/${bookId}/pdf`;
    }
    
    // Carousel auto-play settings
    const carouselElement = document.getElementById('carouselEducationBooks');
    if (carouselElement) {
        // Initialize Bootstrap carousel with custom settings
        const carousel = new bootstrap.Carousel(carouselElement, {
            interval: 3000,
            wrap: true,
            touch: true
        });
    }
    
    // Character counter for syllabus textarea
    const syllabusTextarea = document.getElementById('syllabus');
    if (syllabusTextarea) {
        // Create character counter element
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-muted small text-end mt-1';
        counterDiv.id = 'charCounter';
        counterDiv.textContent = '0 characters';
        
        // Insert after textarea
        syllabusTextarea.parentNode.insertBefore(counterDiv, syllabusTextarea.nextSibling);
        
        // Update counter on input
        syllabusTextarea.addEventListener('input', function() {
            const charCount = this.value.length;
            counterDiv.textContent = `${charCount} characters`;
            
            // Visual feedback on character count
            if (charCount < 20) {
                counterDiv.className = 'text-danger small text-end mt-1';
            } else if (charCount > 5000) {
                counterDiv.className = 'text-warning small text-end mt-1';
            } else {
                counterDiv.className = 'text-muted small text-end mt-1';
            }
        });
    }
    
    // Tooltip initialization (for any tooltips added in the future)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
