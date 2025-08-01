from odoo import fields, models

class BsiPaymentLog(models.Model):
    _name = "bsi.payment.log"
    _description = "BSI Payment Log"
    _order = "received_date desc"

    transaction_id = fields.Char(string="ID Transaksi", required=True)
    va_number = fields.Char(string="Virtual Account", required=True)
    amount = fields.Float(string="Jumlah Pembayaran", required=True)
    status = fields.Char(string="Status", required=True)
    invoice_id = fields.Many2one("account.move", string="Tagihan Terkait", ondelete="set null")
    received_date = fields.Datetime(string="Tanggal Diterima", default=fields.Datetime.now)
    raw_payload = fields.Text(string="Data Mentah JSON")
    note = fields.Text(string="Catatan")
