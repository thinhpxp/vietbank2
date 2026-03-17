import { VxeUI, VxeSwitch, VxeInput, VxeSelect, VxeOption, VxeTextarea, VxeModal, VxeDatePicker, VxePager } from 'vxe-pc-ui'
import { VxeTable, VxeColumn } from 'vxe-table'
import viVN from 'vxe-table/lib/locale/lang/vi-VN'

// Import CSS
import 'vxe-pc-ui/lib/style.css'
import 'vxe-table/lib/style.css'

export function setupVxeTable(app) {
    // Set locale
    VxeUI.setI18n('vi-VN', viVN)
    VxeUI.setLanguage('vi-VN')

    // Global Config cho Modal
    VxeUI.setConfig({
        modal: {
            draggable: true,
            maskStyle: {
                background: 'transparent'
            },
            showFooter: true,
            escClosable: true
        }
    })

    // Register VxeTable components
    app.use(VxeTable)
    app.use(VxeColumn)

    // Register VxeUI components
    app.use(VxeSwitch)
    app.use(VxeInput)
    app.use(VxeSelect)
    app.use(VxeOption)
    app.use(VxeTextarea)
    app.use(VxeModal)
    app.component('VxeDatePicker', VxeDatePicker)
    app.component('vxe-date-picker', VxeDatePicker)
    app.component('VxePager', VxePager)
    app.component('vxe-pager', VxePager)
    VxeUI.component(VxePager)
}
