// Aggressive Manus branding removal script
(function() {
    'use strict';
    
    function removeBranding() {
        // Remove any elements containing "Made with Manus" text
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            if (element.textContent && element.textContent.includes('Made with Manus')) {
                element.style.display = 'none !important';
                element.style.visibility = 'hidden !important';
                element.style.opacity = '0 !important';
                element.remove();
            }
            
            if (element.textContent && element.textContent.includes('Made with')) {
                element.style.display = 'none !important';
                element.style.visibility = 'hidden !important';
                element.style.opacity = '0 !important';
                element.remove();
            }
        });
        
        // Remove fixed positioned elements in bottom right
        const fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position:fixed"]');
        fixedElements.forEach(element => {
            const style = window.getComputedStyle(element);
            if (style.position === 'fixed' && 
                (style.bottom === '20px' || style.right === '20px' || 
                 style.bottom.includes('20') || style.right.includes('20'))) {
                element.style.display = 'none !important';
                element.remove();
            }
        });
        
        // Remove any links to manus
        const manusLinks = document.querySelectorAll('a[href*="manus"]');
        manusLinks.forEach(link => {
            link.style.display = 'none !important';
            link.remove();
        });
        
        // Remove any elements with manus-related attributes
        const manusElements = document.querySelectorAll('[class*="manus"], [id*="manus"], [data-*="manus"]');
        manusElements.forEach(element => {
            element.style.display = 'none !important';
            element.remove();
        });
    }
    
    // Run immediately
    removeBranding();
    
    // Run after DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeBranding);
    }
    
    // Run periodically to catch dynamically added elements
    setInterval(removeBranding, 1000);
    
    // Use MutationObserver to catch new elements
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                removeBranding();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();

