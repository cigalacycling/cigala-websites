// Vivify Sports welcome form as a branded, fillable Word document (Marine 17 Nov 2026: "just as a Word I can send clients").
// Questions: vivify/forms/welcome-form-questions.json (from Marine's form; no client answers).
//   node tools/vivify_welcome_docx.js   -> vivify/forms/Vivify-Sports-Welcome-Form.docx
const fs = require('fs'), path = require('path');
const D = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, ImageRun,
        Header, Footer, AlignmentType, PageNumber, CheckBox, VerticalAlign, HeightRule, TableLayoutType } = D;
const R = path.resolve(__dirname, '..') + '/vivify/';
const spec = JSON.parse(fs.readFileSync(R + 'forms/welcome-form-questions.json'));
const TEAL = '19444B', DEEP = '0C2226', AQUA = 'B1D8DD', LIME = '80A315', SOFT = 'EEF6F7', GREY = '5F7A7E', FONT = 'Arial';
const W = 9906, C1 = 3600, C2 = W - C1;                        // A4 with 1000 twip margins
const logo = fs.readFileSync(fs.readdirSync(R + 'img-orig').filter(f => f.startsWith('0e1488_f038fcb12444476fab18be6dc4bf29e1')).map(f => R + 'img-orig/' + f)[0]);
const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, color: o.color || '1F2A2C', italics: o.italics, allCaps: o.caps });
const P = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [children], spacing: { before: o.before || 0, after: o.after ?? 80 },
                                                   alignment: o.align, shading: o.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: o.fill } : undefined,
                                                   indent: o.indent, keepNext: o.keepNext, border: o.border });
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const line = { style: BorderStyle.SINGLE, size: 4, color: 'D5E4E6' };
const cellBorders = { top: line, bottom: line, left: line, right: line };
const box = () => new CheckBox({ checked: false, checkedState: { value: '2612' }, uncheckedState: { value: '2610' } });

function qRow(label, answerChildren, height) {
  return new TableRow({ cantSplit: true, height: height ? { value: height, rule: HeightRule.ATLEAST } : undefined, children: [
    new TableCell({ width: { size: C1, type: WidthType.DXA }, borders: cellBorders, margins: { top: 90, bottom: 90, left: 120, right: 120 },
                    verticalAlign: VerticalAlign.TOP, children: [P(t(label, { bold: true, size: 19, color: DEEP }), { after: 0 })] }),
    new TableCell({ width: { size: C2, type: WidthType.DXA }, borders: cellBorders, margins: { top: 90, bottom: 90, left: 120, right: 120 },
                    shading: { type: ShadingType.CLEAR, color: 'auto', fill: SOFT }, children: answerChildren })] });
}
function noteRow(text) {
  return new TableRow({ cantSplit: true, children: [new TableCell({ columnSpan: 2, width: { size: W, type: WidthType.DXA }, borders: cellBorders,
    margins: { top: 100, bottom: 60, left: 120, right: 120 }, children: [P(t(text, { bold: true, size: 18, color: LIME, caps: true }), { after: 0 })] })] });
}
function options(opts) {
  const runs = [];
  opts.forEach((o, i) => { runs.push(box(), t('\u00A0' + o.replace(/ /g, '\u00A0').replace(/-/g, '\u2011') + (i < opts.length - 1 ? '      ' : ''), { size: 19 })); });   // no break inside an option
  return [new Paragraph({ children: runs, spacing: { after: 0, line: 300 } })];
}
function sectionHead(title) {
  return P(t(' ' + title, { bold: true, size: 24, color: 'FFFFFF', caps: true }), { fill: TEAL, before: 280, after: 120, keepNext: true });
}
function table(rows) {
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [C1, C2], layout: TableLayoutType.FIXED, rows });
}
const body = [];
// title block
body.push(new Paragraph({ children: [new ImageRun({ type: 'png', data: logo, transformation: { width: 96, height: 90 } })], spacing: { after: 160 } }));
body.push(P(t('Welcome Form', { bold: true, size: 52, color: TEAL, caps: true }), { after: 40 }));
body.push(P(t('Nutrition Performance Intake', { bold: true, size: 24, color: LIME, caps: true }), { after: 200,
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: AQUA, space: 8 } } }));
body.push(P(t('This form is designed to assess your training demands, lifestyle, dietary habits, and health status. The information collected allows me to create an individualized, evidence-based nutrition plan to optimize performance, recovery, body composition, and long-term health.', { size: 20 }), { after: 120 }));
body.push(P([t('How to fill it in: ', { bold: true, size: 20, color: TEAL }), t('type your answers in the shaded boxes and tick the boxes that apply. Then save the document and email it back to ', { size: 20 }),
             t('marine@vivifysports.com', { bold: true, size: 20, color: TEAL }), t('. Please answer as fully as you can; everything you share stays private.', { size: 20 })], { after: 120 }));
for (const [title, fields] of spec.S) {
  body.push(sectionHead(title));
  const rows = [];
  for (const f of fields) {
    const [kind, name, label, opts] = f;
    if (kind === 'note') { rows.push(noteRow(name)); continue; }
    if (kind === 'radio' || kind === 'check') rows.push(qRow(label, options(opts)));
    else if (kind === 'area') rows.push(qRow(label, [P(t(''), { after: 0 })], 1100));
    else rows.push(qRow(label.replace(/ \*$/, ''), [P(t(''), { after: 0 })], 420));
  }
  body.push(table(rows));
}
// declaration
body.push(sectionHead('11. Declaration & Consent'));
body.push(new Paragraph({ children: [box(), t('  ' + spec.DECL, { size: 20 })], spacing: { after: 120 } }));
body.push(new Paragraph({ children: [box(), t('  I consent to Vivify Sports using the health information in this form to prepare my nutrition coaching. It is kept private and not shared with anyone else.', { size: 20 })], spacing: { after: 200 } }));
body.push(table([qRow('Signature (type your full name)', [P(t(''), { after: 0 })], 520), qRow('Date', [P(t(''), { after: 0 })], 420)]));
body.push(P(t('Thank you! Please save this document and email it to marine@vivifysports.com before your first session.', { bold: true, size: 20, color: TEAL }), { before: 240 }));

const doc = new Document({
  creator: 'Vivify Sports', title: 'Vivify Sports Welcome Form', description: 'Nutrition Performance Intake',
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000, header: 500, footer: 500 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 },
      children: [t('VIVIFY SPORTS', { bold: true, size: 16, color: TEAL }), t('   ·   Welcome Form', { size: 16, color: GREY })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
      border: { top: { style: BorderStyle.SINGLE, size: 6, color: AQUA, space: 6 } },
      children: [t('Vivify Sports  ·  marine@vivifysports.com  ·  +353 87 224 7402  ·  vivifysports.com  ·  Page ', { size: 15, color: GREY }),
                 new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 15, color: GREY })] })] }) },
    children: body }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(R + 'forms/Vivify-Sports-Welcome-Form.docx', b); console.log('written', b.length); });
