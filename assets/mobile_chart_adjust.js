// Mobile detection and chart title font size adjustment
(function() {
    function isMobile() {
        return window.innerWidth <= 768 || 
               /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    function adjustChartTitles() {
        if (!isMobile()) return;
        
        // Find all Plotly graph containers
        const graphContainers = document.querySelectorAll('.js-plotly-plot, [id*="graph"], [id*="Graph"]');
        
        graphContainers.forEach(function(container) {
            if (window.Plotly) {
                try {
                    // Use Plotly's API to get the figure data
                    const figure = window.Plotly.Plots.resize(container);
                    
                    // Try to get layout from the container's data attribute or Plotly's internal storage
                    let layout = null;
                    if (container.data && container.layout) {
                        layout = container.layout;
                    } else if (container._fullLayout) {
                        layout = container._fullLayout;
                    }
                    
                    if (layout && layout.title) {
                        // Get current title font size
                        let currentSize = 28; // default
                        if (layout.title.font && typeof layout.title.font.size === 'number') {
                            currentSize = layout.title.font.size;
                        } else if (layout.title.font && layout.title.font.size) {
                            currentSize = parseInt(layout.title.font.size) || 28;
                        }
                        
                        // Reduce title font size for mobile
                        let newSize = currentSize;
                        if (currentSize >= 28) {
                            newSize = 18;
                        } else if (currentSize >= 24) {
                            newSize = 16;
                        } else if (currentSize >= 20) {
                            newSize = 14;
                        }
                        
                        // Only update if size needs to change and hasn't been adjusted yet
                        if (newSize !== currentSize && !container._mobileAdjusted) {
                            window.Plotly.relayout(container, {
                                'title.font.size': newSize
                            });
                            container._mobileAdjusted = true;
                        }
                    }
                } catch(e) {
                    // Try alternative approach: directly update via relayout with known structure
                    try {
                        if (!container._mobileAdjusted) {
                            // Apply mobile font size reduction directly
                            window.Plotly.relayout(container, {
                                'title.font.size': 18  // Default mobile size
                            });
                            container._mobileAdjusted = true;
                        }
                    } catch(e2) {
                        // Silently fail if chart not ready
                    }
                }
            }
        });
    }
    
    // Function to run adjustment with retries
    function runAdjustment() {
        adjustChartTitles();
        // Retry a few times to catch charts that load asynchronously
        let retries = 0;
        const maxRetries = 8;
        const retryInterval = setInterval(function() {
            retries++;
            adjustChartTitles();
            if (retries >= maxRetries) {
                clearInterval(retryInterval);
            }
        }, 800);
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(runAdjustment, 800);
        });
    } else {
        setTimeout(runAdjustment, 800);
    }
    
    // Also run on window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Reset adjustment flag on resize to allow re-adjustment
            document.querySelectorAll('.js-plotly-plot, [id*="graph"], [id*="Graph"]').forEach(function(container) {
                container._mobileAdjusted = false;
            });
            adjustChartTitles();
        }, 250);
    });
    
    // Use MutationObserver to detect when new charts are added
    const observer = new MutationObserver(function(mutations) {
        let shouldAdjust = false;
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && (node.classList.contains('js-plotly-plot') || 
                        node.querySelector && node.querySelector('.js-plotly-plot'))) {
                        shouldAdjust = true;
                    }
                });
            }
        });
        if (shouldAdjust) {
            setTimeout(adjustChartTitles, 500);
        }
    });
    
    // Start observing
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }
})();

