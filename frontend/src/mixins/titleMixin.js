function getTitle(vm) {
    const { title } = vm.$options
    if (title) {
        return typeof title === 'function'
            ? title.call(vm)
            : title
    }
}

export default {
    created() {
        const title = getTitle(this)
        if (title) {
            document.title = `${title}`
        }
    },
    // Hỗ trợ cập nhật tiêu đề khi dữ liệu thay đổi nếu title là một function
    updated() {
        const title = getTitle(this)
        if (title) {
            document.title = `${title}`
        }
    }
}
