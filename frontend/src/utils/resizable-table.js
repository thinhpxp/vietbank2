export function makeTableResizable(table, tableId) {
    if (!table) return;

    // Thiết lập table-layout: fixed để việc co kéo chính xác hơn
    table.style.tableLayout = 'fixed';
    table.style.width = '100%';

    const headers = table.querySelectorAll('th');
    const storageKey = `table_widths_${tableId || 'default'}`;

    // 1. Tải độ rộng đã lưu từ localStorage
    const savedWidths = JSON.parse(localStorage.getItem(storageKey) || '{}');

    let thBeingResized = null;
    let startX, startWidth;

    // Tạo đường kẻ dọc ảo (Guide Line)
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

    headers.forEach((th, index) => {
        // Áp dụng độ rộng đã lưu nếu có
        if (savedWidths[index]) {
            th.style.width = savedWidths[index];
        }

        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'resize-handle';
        resizeHandle.style.position = 'absolute';
        resizeHandle.style.right = '0';
        resizeHandle.style.top = '0';
        resizeHandle.style.width = '6px';
        resizeHandle.style.height = '100%';
        resizeHandle.style.cursor = 'col-resize';
        resizeHandle.style.userSelect = 'none';
        resizeHandle.style.zIndex = '10';

        th.style.position = 'relative';
        th.appendChild(resizeHandle);

        // Sự kiện mousedown để bắt đầu kéo
        resizeHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            e.preventDefault();

            thBeingResized = th;
            startX = e.pageX;
            startWidth = thBeingResized.offsetWidth;

            // Hiển thị đường kẻ dọc
            guideLine.style.left = `${e.pageX}px`;
            guideLine.style.display = 'block';

            document.body.style.cursor = 'col-resize';

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        // Tính năng Double Click để Auto-fit
        resizeHandle.addEventListener('dblclick', () => {
            th.style.width = 'auto';
            saveWidths();
        });
    });

    const onMouseMove = (e) => {
        if (!thBeingResized) return;

        const delta = e.pageX - startX;
        const newWidth = startWidth + delta;

        if (newWidth > 50) {
            thBeingResized.style.width = `${newWidth}px`;
            guideLine.style.left = `${e.pageX}px`;
        }
    };

    const onMouseUp = () => {
        if (thBeingResized) {
            saveWidths();
        }

        thBeingResized = null;
        guideLine.style.display = 'none';
        document.body.style.cursor = '';

        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };

    function saveWidths() {
        const currentWidths = {};
        headers.forEach((th, index) => {
            currentWidths[index] = th.style.width || `${th.offsetWidth}px`;
        });
        localStorage.setItem(storageKey, JSON.stringify(currentWidths));
    }
}