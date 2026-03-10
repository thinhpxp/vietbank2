/**
 * Formula Engine — Parse và tính toán công thức
 * Hỗ trợ: SUM, COUNT, AVG, MIN, MAX, CONCAT, ROUND, IF, MUL, SUB, DIV
 */

export function evaluateFormula(formula, sections) {
    if (!formula || !formula.trim().startsWith('=')) return null;
    const expr = formula.trim().substring(1);
    return evaluateSubExpr(expr, sections);
}

function evaluateSubExpr(expr, sections) {
    if (!expr) return null;
    const match = expr.trim().match(/^(\w+)\((.*)\)$/s);
    if (!match) return null;
    const func = match[1].toUpperCase();
    const argsRaw = match[2];
    const args = parseFormulaArgs(argsRaw);

    const collectRaw = (argStr) => {
        if (!argStr) return [];
        const trimmed = argStr.trim();
        if (trimmed.startsWith('"') || trimmed.startsWith("'")) {
            return [trimmed.replace(/['"]/g, '')];
        }

        if (trimmed.includes('(') && trimmed.includes(')')) {
            const res = evaluateSubExpr(trimmed, sections);
            return res !== null ? [res] : [];
        }

        let results = [];
        let typeCode = null;
        let fieldKey = trimmed;
        if (trimmed.includes('.')) {
            const parts = trimmed.split('.');
            typeCode = parts[0].toUpperCase();
            fieldKey = parts[1];
        }

        const extractFromObj = (obj, fk) => {
            const fv = obj.individual_field_values || obj.field_values || obj;
            const actualKey = Object.keys(fv).find(k => k.toLowerCase() === fk.toLowerCase());
            return actualKey ? fv[actualKey] : null;
        };

        if (typeCode === 'ASSET' || !typeCode) {
            Object.keys(sections).forEach(sKey => {
                if (sKey !== '_GENERAL_' && sKey !== 'PERSON' && Array.isArray(sections[sKey]) && !sKey.endsWith('_list')) {
                    sections[sKey].forEach(obj => {
                        const v = extractFromObj(obj, fieldKey);
                        if (v !== null && v !== undefined) results.push(v);
                    });
                }
            });
        }
        if (typeCode === 'PERSON' || (!typeCode && results.length === 0)) {
            const people = sections['PERSON'] || sections['people'] || [];
            if (Array.isArray(people)) {
                people.forEach(obj => {
                    const v = extractFromObj(obj, fieldKey);
                    if (v !== null && v !== undefined) results.push(v);
                });
            }
        }
        if (typeCode === '_GENERAL_' || (!typeCode && results.length === 0)) {
            const gen = sections['_GENERAL_'];
            if (gen) {
                const v = extractFromObj(gen, fieldKey);
                if (v !== null && v !== undefined) results.push(v);
            }
        }
        if (typeCode && !['ASSET', 'PERSON', '_GENERAL_'].includes(typeCode)) {
            const sKey = Object.keys(sections).find(k => k.toUpperCase() === typeCode);
            if (sKey && Array.isArray(sections[sKey])) {
                sections[sKey].forEach(obj => {
                    const v = extractFromObj(obj, fieldKey);
                    if (v !== null && v !== undefined) results.push(v);
                });
            }
        }
        return results;
    };

    const toFloat = (val) => {
        if (val === null || val === undefined || val === '') return 0;
        if (typeof val === 'number') return val;
        let s = String(val).replace(/\s/g, '').replace(/\u00a0/g, '').trim();
        if (!s) return 0;

        if (s.includes(',') && s.includes('.')) {
            if (s.lastIndexOf(',') > s.lastIndexOf('.')) {
                s = s.replace(/\./g, '').replace(/,/g, '.');
            } else {
                s = s.replace(/,/g, '');
            }
        } else if (s.includes(',')) {
            const count = (s.match(/,/g) || []).length;
            const parts = s.split(',');
            if (count > 1) s = s.replace(/,/g, '');
            else if (parts[1].length === 3) s = s.replace(/,/g, '');
            else s = s.replace(/,/g, '.');
        } else if (s.includes('.')) {
            const count = (s.match(/\./g) || []).length;
            const parts = s.split('.');
            if (count > 1) s = s.replace(/\./g, '');
            else if (parts[1].length === 3) s = s.replace(/\./g, '');
        }

        const n = parseFloat(s);
        return isNaN(n) ? 0 : n;
    };

    const collectNumbers = (argList) => {
        const nums = [];
        argList.forEach(a => {
            const raws = collectRaw(a);
            if (raws.length === 0) {
                nums.push(toFloat(a));
            } else {
                raws.forEach(r => nums.push(toFloat(r)));
            }
        });
        return nums;
    };

    const collectTexts = (argList, separator) => {
        const texts = [];
        argList.forEach(a => {
            const raws = collectRaw(a);
            raws.forEach(r => { if (r !== null && r !== undefined) texts.push(String(r)); });
        });
        return texts.join(separator);
    };

    switch (func) {
        case 'SUM': {
            const vals = collectNumbers(args);
            return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) : 0;
        }
        case 'PRODUCT':
        case 'MUL': {
            const vals = collectNumbers(args);
            return vals.length > 0 ? vals.reduce((a, b) => a * b, 1) : 0;
        }
        case 'SUBTRACT':
        case 'SUB': {
            const vals = collectNumbers(args);
            if (vals.length === 0) return 0;
            let res = vals[0];
            for (let i = 1; i < vals.length; i++) res -= vals[i];
            return res;
        }
        case 'DIVIDE':
        case 'DIV': {
            const vals = collectNumbers(args);
            if (vals.length === 0) return 0;
            let res = vals[0];
            for (let i = 1; i < vals.length; i++) {
                if (vals[i] !== 0) res /= vals[i];
            }
            return res;
        }
        case 'ROUND': {
            const vals = collectNumbers(args.slice(0, 1));
            if (vals.length === 0) return 0;
            const pRaw = args.length > 1 ? evaluateSubExpr(args[1], sections) || args[1] : 0;
            const precision = parseInt(String(pRaw).replace(/['"]/g, ''));
            const factor = Math.pow(10, isNaN(precision) ? 0 : precision);
            return Math.round(vals[0] * factor) / factor;
        }
        case 'COUNT': {
            let total = 0;
            args.forEach(arg => {
                const trimmed = arg.trim();
                const typeCode = trimmed.includes('.') ? trimmed.split('.')[0].toUpperCase() : trimmed.toUpperCase();
                if (typeCode === 'ASSET') {
                    Object.keys(sections).forEach(k => {
                        if (k !== '_GENERAL_' && k !== 'PERSON' && Array.isArray(sections[k]) && !k.endsWith('_list')) {
                            total += sections[k].length;
                        }
                    });
                } else if (typeCode === 'PERSON') {
                    const p = sections['PERSON'] || [];
                    if (Array.isArray(p)) total += p.length;
                } else {
                    const sKey = Object.keys(sections).find(k => k.toUpperCase() === typeCode);
                    if (sKey && Array.isArray(sections[sKey])) total += sections[sKey].length;
                }
            });
            return total;
        }
        case 'AVG': {
            const vals = collectNumbers(args);
            return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
        }
        case 'MIN': {
            const vals = collectNumbers(args);
            return vals.length > 0 ? Math.min(...vals) : 0;
        }
        case 'MAX': {
            const vals = collectNumbers(args);
            return vals.length > 0 ? Math.max(...vals) : 0;
        }
        case 'CONCAT': {
            const sepArg = args.find(a => a.trim().startsWith('"') || a.trim().startsWith("'"));
            const separator = sepArg ? sepArg.trim().replace(/["']/g, '') : ', ';
            const fieldArgs = args.filter(a => a !== sepArg);
            return collectTexts(fieldArgs, separator);
        }
        case 'IF': {
            if (args.length < 3) return '';
            const condRaw = args[0].trim();
            let isTrue = false;
            let ops = ['>=', '<=', '>', '<', '='];
            let usedOp = ops.find(op => condRaw.includes(op));
            if (usedOp) {
                const [lS, rS] = condRaw.split(usedOp);
                const lV = collectNumbers([lS.trim()])[0] || 0;
                const rV = collectNumbers([rS.trim()])[0] || 0;
                if (usedOp === '>=') isTrue = lV >= rV;
                else if (usedOp === '<=') isTrue = lV <= rV;
                else if (usedOp === '>') isTrue = lV > rV;
                else if (usedOp === '<') isTrue = lV < rV;
                else if (usedOp === '=') isTrue = Math.abs(lV - rV) < 0.000001 || String(lV) === String(rV);
            } else {
                const rawCond = collectRaw(condRaw);
                isTrue = !!(rawCond[0] || condRaw.replace(/['"]/g, ''));
            }
            const resKey = isTrue ? args[1] : args[2];
            const lookup = collectRaw(resKey);
            return lookup.length > 0 ? lookup[0] : resKey.trim().replace(/['"]/g, '');
        }
        default: return '';
    }
}

function parseFormulaArgs(raw) {
    if (!raw) return [];
    const args = [];
    let current = '';
    let inQuote = false;
    let quoteChar = '';
    let depth = 0;
    for (let i = 0; i < raw.length; i++) {
        const ch = raw[i];
        if ((ch === '"' || ch === "'") && !inQuote) {
            inQuote = true; quoteChar = ch; current += ch;
        } else if (ch === quoteChar && inQuote) {
            inQuote = false; current += ch;
        } else if (!inQuote) {
            if (ch === '(') depth++;
            else if (ch === ')') depth--;
            if (ch === ',' && depth === 0) {
                args.push(current.trim()); current = '';
                continue;
            }
            current += ch;
        } else {
            current += ch;
        }
    }
    if (current.trim()) args.push(current.trim());
    return args;
}
