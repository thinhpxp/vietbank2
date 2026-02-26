import { VxeUI } from 'vxe-pc-ui'
import { VxeTable, VxeColumn } from 'vxe-table'
import viVN from 'vxe-table/lib/locale/lang/vi-VN'

// Import CSS
import 'vxe-pc-ui/lib/style.css'
import 'vxe-table/lib/style.css'

export function setupVxeTable(app) {
    // Set locale
    VxeUI.setI18n('vi-VN', viVN)
    VxeUI.setLanguage('vi-VN')

    // Register VxeUI and Table components
    app.use(VxeUI)
    app.use(VxeTable)
    app.use(VxeColumn)
}
