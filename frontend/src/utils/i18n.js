/**
 * I18N Utility for Frontend Translation
 * Dictionnary for system codes to Vietnamese labels
 */

const dictionary = {
    // Entities / Object Types
    'PERSON': 'Cá nhân',
    'ASSET': 'Tài sản',
    'SAVINGS': 'Sổ tiết kiệm/Tiền gửi',
    'REALESTATE': 'Bất động sản',
    'VEHICLE': 'Phương tiện vận tải',
    'BOND': 'Trái phiếu',
    'INSURANCE': 'Bảo hiểm',
    'ATTORNEY': 'Người đại diện/Ủy quyền',
    'CONTRACT_HDTD_TL': 'HĐTD Từng lần',
    'CONTRACT_HDTD_HM': 'HĐTD Hạn mức',
    'CONTRACT_HDTC': 'HĐ Thế chấp',

    // Roles / Relations
    'OWNER': 'Chủ sở hữu',
    'CO_OWNER': 'Đồng sở hữu',
    'SPOUSE': 'Vợ/Chồng',
    'GUARANTOR': 'Người bảo lãnh',
    'BORROWER': 'Người vay',
    'CO_BORROWER': 'Người đồng vay',
    'SECURES': 'Bảo đảm cho',
    'AMENDS': 'Sửa đổi cho',
    'REFERENCES': 'Dẫn chiếu đến',


    // Statuses
    'DRAFT': 'Bản nháp',
    'FINALIZED': 'Đã khóa',

    // Common labels
    'ACTIONS': 'Thao tác',
    'EDIT': 'Sửa',
    'DELETE': 'Xóa',
    'SUCCESS': 'Thành công',
    'ERROR': 'Lỗi',

    // Additional variants
    'LOAN_CONTRACT_CREDIT_LINE': 'HĐTD Hạn mức',
    'REAL_ESTATE': 'Bất động sản',
    'MORTGAGE_CONTRACT': 'Hợp đồng Thế chấp',

    // Modal UI Labels
    'CHI_TIET_DOI_TUONG': 'Chi tiết đối tượng',
    'THONG_TIN_CHUNG': 'Thông tin chung',
    'LOAI_DOI_TUONG': 'Loại đối tượng',
    'TEN_HIEN_THI': 'Tên hiển thị',
    'THUO_TINH_CHI_TIET': 'Thuộc tính chi tiết',
    'TRUONG_DU_LIEU': 'Trường dữ liệu',
    'GIA_TRI': 'Giá trị',
    'KHONG_CO_DU_LIEU_CHI_TIET': 'Không có dữ liệu chi tiết',
    'LOI_TAI_DU_LIEU': 'Lỗi tải dữ liệu',
    'DONG': 'Đóng',

    // Specific Field Fallbacks
    'so_hop_dong': 'Số hợp đồng',

    // Error Messages
    'YOU DO NOT HAVE PERMISSION TO PERFORM THIS ACTION.': 'Bạn không có quyền thực hiện hành động này.',
    'AUTHENTICATION CREDENTIALS WERE NOT PROVIDED.': 'Thông tin xác thực không được cung cấp.',
};

/**
 * Translate a key to Vietnamese using the dictionary.
 * Supports smart translation of patterns like "Name (CODE)"
 * @param {string} key - The system code or English string
 * @returns {string} - The translated string
 */
export function translate(key) {
    if (!key) return '';

    const strKey = String(key);

    // 1. Exact match
    const upperKey = strKey.toUpperCase();
    if (dictionary[upperKey]) return dictionary[upperKey];

    // 2. Smart match for pattern: "Text (CODE)"
    // Matches something like "John Doe (PERSON)" or "HĐ 123 (CONTRACT_HDTC)"
    const parenthesizedMatch = strKey.match(/^(.*)\(([^)]+)\)$/);
    if (parenthesizedMatch) {
        const prefix = parenthesizedMatch[1];
        const code = parenthesizedMatch[2].toUpperCase();
        if (dictionary[code]) {
            return `${prefix}(${dictionary[code]})`;
        }
    }

    return key;
}


export default {
    install: (app) => {
        // Register as global property for templates: {{ $t(key) }}
        app.config.globalProperties.$t = translate;
    }
};
