/**
 * Chuyển số thành chữ (JS Implementation)
 */
export function numberToWords(val) {
    if (val === undefined || val === null || val === "") return "";
    if (val === 0 || val === '0') return "Không";
    let sVal = val.toString().replace(',', '.'); // Chuẩn hóa dấu phẩy thành chấm
    if (!/[0-9]/.test(sVal)) return "";

    const units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];
    const placeValues = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"];

    const readThreeDigits = (n, showZeroHundred) => {
        let res = "";
        const hundred = Math.floor(n / 100);
        const ten = Math.floor((n % 100) / 10);
        const unit = n % 10;
        if (hundred > 0) {
            res += units[hundred] + " trăm ";
        } else if (showZeroHundred) {
            res += "không trăm ";
        }
        if (ten > 1) {
            res += units[ten] + " mươi ";
        } else if (ten === 1) {
            res += "mười ";
        } else if ((hundred > 0 || showZeroHundred) && unit > 0 && ten === 0) {
            res += "lẻ ";
        }
        if (unit === 1 && ten > 1) {
            res += "mốt";
        } else if (unit === 5 && ten > 0) {
            res += "lăm";
        } else if (unit > 0) {
            res += units[unit];
        }
        return res.trim();
    };

    const readInteger = (sNum) => {
        if (sNum === "0" || sNum === "") return "không";
        let chunks = [];
        let temp = sNum;
        while (temp.length > 0) {
            chunks.push(parseInt(temp.slice(-3)));
            temp = temp.slice(0, -3);
        }
        let res = "";
        for (let i = chunks.length - 1; i >= 0; i--) {
            if (chunks[i] > 0) {
                res += readThreeDigits(chunks[i], i < chunks.length - 1) + " " + placeValues[i] + " ";
            }
        }
        return res.trim();
    };

    // Tách phần nguyên và phần thập phân
    const parts = sVal.split('.');
    const integerPart = parts[0].replace(/\D/g, '') || "0";
    const decimalPart = parts.length > 1 ? parts[1].replace(/\D/g, '') : "";

    let result = readInteger(integerPart);

    if (decimalPart) {
        result += " phẩy";
        for (let i = 0; i < decimalPart.length; i++) {
            const digit = parseInt(decimalPart[i]);
            result += " " + (digit === 0 ? "không" : units[digit]);
        }
    }

    const finalResult = result.trim();
    return finalResult.charAt(0).toUpperCase() + finalResult.slice(1);
}

/**
 * Định dạng số theo chuẩn VN (phân tách hàng nghìn bằng dấu chấm, thập phân bằng dấu phẩy)
 */
export function formatNumberVN(val) {
    if (val === undefined || val === null || val === '') return '';
    const sVal = val.toString();
    const parts = sVal.split('.');

    const integerPart = parts[0].replace(/\D/g, '') || "0";
    let formattedInt = new Intl.NumberFormat('en-US').format(parseInt(integerPart));
    formattedInt = formattedInt.replace(/,/g, '.');

    if (parts.length > 1) {
        return formattedInt + ',' + parts[1].replace(/\D/g, '');
    }
    return formattedInt;
}

/**
 * Parse giá trị thô từ input text (VN format) về số JS chuẩn (dot decimal)
 */
export function parseNumberVN(rawValue) {
    let clean = rawValue.replace(/\./g, '');
    clean = clean.replace(',', '.');
    clean = clean.replace(/[^0-9.]/g, '');
    const parts = clean.split('.');
    if (parts.length > 2) {
        clean = parts[0] + '.' + parts.slice(1).join('');
    }
    return clean;
}
