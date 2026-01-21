export function makeTableResizable(table, tableId) {
    if (!table) return;

    // Table-layout fixed helps with precise resizing
    table.style.tableLayout = 'fixed';
    // Use max-content so table can grow beyond 100% and trigger scroll-wrapper
    table.style.width = 'max-content';
    table.style.minWidth = '100%';

    const headers = table.querySelectorAll('th');
    const storageKey = `table_widths_${tableId || 'default'}`;

    // 1. Load saved state from localStorage
    const savedState = JSON.parse(localStorage.getItem(storageKey) || '{}');
    const savedWidths = savedState.widths || {};
    const savedTableWidth = savedState.tableWidth;

    // Apply saved column widths
    headers.forEach((th, index) => {
        if (savedWidths[index]) {
            th.style.width = savedWidths[index];
        }
    });

    // Apply saved table width if it exists
    if (savedTableWidth) {
        table.style.width = savedTableWidth;
    }

    let thBeingResized = null;
    let startX, startWidth;

    const minWidth = 50;
    let hasMoved = false;

    // Transparent overlay to prevent all other interactions during resize
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.zIndex = '9998';
    overlay.style.display = 'none';
    overlay.style.cursor = 'col-resize';
    document.body.appendChild(overlay);

    // Virtual guide line
    const guideLine = document.createElement('div');
    guideLine.style.position = 'fixed';
    guideLine.style.top = '0';
    guideLine.style.width = '1px';
    guideLine.style.height = '100vh';
    guideLine.style.backgroundColor = '#3498db';
    guideLine.style.zIndex = '9999';
    guideLine.style.display = 'none';
    guideLine.style.pointerEvents = 'none';
    document.body.appendChild(guideLine);

    headers.forEach((th) => {
        // Create handle
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'resize-handle';
        resizeHandle.style.position = 'absolute';
        resizeHandle.style.right = '0';
        resizeHandle.style.top = '0';
        resizeHandle.style.width = '8px';
        resizeHandle.style.height = '100%';
        resizeHandle.style.cursor = 'col-resize';
        resizeHandle.style.userSelect = 'none';
        resizeHandle.style.zIndex = '10';
        resizeHandle.style.transition = 'background 0.2s';

        th.style.position = 'relative';
        th.appendChild(resizeHandle);

        // Hover effect for handle
        resizeHandle.addEventListener('mouseenter', () => {
            resizeHandle.style.backgroundColor = 'rgba(52, 152, 219, 0.3)';
        });
        resizeHandle.addEventListener('mouseleave', () => {
            if (!thBeingResized) {
                resizeHandle.style.backgroundColor = 'transparent';
            }
        });

        // Prevent click from bubbling to TH (which would trigger sorting)
        resizeHandle.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        resizeHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            e.preventDefault();

            thBeingResized = th;
            startX = e.pageX;
            startWidth = thBeingResized.offsetWidth;
            hasMoved = false;

            document.body.classList.add('is-resizing');
            overlay.style.display = 'block';

            resizeHandle.style.backgroundColor = 'rgba(52, 152, 219, 0.6)';

            guideLine.style.left = `${e.pageX}px`;
            guideLine.style.display = 'block';

            document.body.style.cursor = 'col-resize';

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        // Double Click to Auto-fit (Reset)
        resizeHandle.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            th.style.width = 'auto';
            // Also reset table width to allow max-content to take over
            table.style.width = 'max-content';
            saveState();
        });
    });

    const onMouseMove = (e) => {
        if (!thBeingResized) return;

        const delta = e.pageX - startX;
        if (Math.abs(delta) > 2) {
            hasMoved = true;
        }

        let newWidth = startWidth + delta;

        if (newWidth < minWidth) newWidth = minWidth;

        thBeingResized.style.width = `${newWidth}px`;

        // Sum-based: Sync table width to total headers width
        updateTableWidth();

        guideLine.style.left = `${e.pageX}px`;
    };

    const onMouseUp = () => {
        if (thBeingResized) {
            saveState();
            // Reset background for all handles
            table.querySelectorAll('.resize-handle').forEach(h => {
                h.style.backgroundColor = 'transparent';
            });

            // If we actually resized, prevent any click event from triggering sorting
            if (hasMoved) {
                // We use a capture phase listener on the overlay or window to stop the follow-up click
                // But since we have an overlay, the click will happen on the overlay!
                // So the <th> will never receive a click event.
            }
        }

        thBeingResized = null;
        guideLine.style.display = 'none';
        overlay.style.display = 'none';
        document.body.classList.remove('is-resizing');
        document.body.style.cursor = '';

        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };

    // Kill any clicks on the overlay just in case
    overlay.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
    });

    function updateTableWidth() {
        let total = 0;
        table.querySelectorAll('th').forEach(th => {
            total += th.offsetWidth;
        });
        table.style.width = `${total}px`;
    }

    function saveState() {
        const widths = {};
        headers.forEach((th, index) => {
            widths[index] = th.style.width || `${th.offsetWidth}px`;
        });

        const state = {
            widths,
            tableWidth: table.style.width
        };
        localStorage.setItem(storageKey, JSON.stringify(state));
    }
}
