export function makeTableResizable(table) {
    if (!table) return;

    const headers = table.querySelectorAll('th');
    let thBeingResized = null;
    let startX, startWidth;

    headers.forEach(th => {
        const resizeHandle = document.createElement('div');
        resizeHandle.style.position = 'absolute';
        resizeHandle.style.right = '0';
        resizeHandle.style.top = '0';
        resizeHandle.style.width = '5px';
        resizeHandle.style.height = '100%';
        resizeHandle.style.cursor = 'col-resize';
        resizeHandle.style.userSelect = 'none';

        th.style.position = 'relative'; // Cần thiết để handle được định vị đúng
        th.appendChild(resizeHandle);

        resizeHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation(); // Ngăn sự kiện sort của header
            thBeingResized = th;
            startX = e.pageX;
            startWidth = thBeingResized.offsetWidth;
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    });

    const onMouseMove = (e) => {
        if (!thBeingResized) return;
        const newWidth = startWidth + (e.pageX - startX);
        if (newWidth > 40) { // Đặt độ rộng tối thiểu
            thBeingResized.style.width = `${newWidth}px`;
        }
    };

    const onMouseUp = () => {
        thBeingResized = null;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };
}