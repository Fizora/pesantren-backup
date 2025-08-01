import logging
import json
import requests
from odoo.exceptions import UserError
from ..utils.bsi_encryption import BSIEncryption
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class CdnInvoice(models.Model):
    _inherit = "account.move"

    va_number = fields.Char(string="Virtual Account BSI", readonly=True)
    show_generate_va = fields.Boolean(compute="_compute_va_button_visibility")
    show_update_va = fields.Boolean(compute="_compute_va_button_visibility")
    show_inquiry_va = fields.Boolean(compute="_compute_va_button_visibility")
    santri_id = fields.Many2one("res.partner", string="Santri")

    @api.depends("va_number")
    def _compute_va_button_visibility(self):
        for rec in self:
            rec.show_generate_va = not rec.va_number
            rec.show_update_va = bool(rec.va_number)
            rec.show_inquiry_va = bool(rec.va_number)




class CdnInvoice(models.Model):
    _inherit = "account.move"

    va_number = fields.Char(string="Virtual Account BSI", readonly=True)
    show_generate_va = fields.Boolean(compute="_compute_va_button_visibility")
    show_update_va = fields.Boolean(compute="_compute_va_button_visibility")
    show_inquiry_va = fields.Boolean(compute="_compute_va_button_visibility")
    santri_id = fields.Many2one("res.partner", string="Santri")

    @api.depends("va_number")
    def _compute_va_button_visibility(self):
        for rec in self:
            rec.show_generate_va = not rec.va_number
            rec.show_update_va = bool(rec.va_number)
            rec.show_inquiry_va = bool(rec.va_number)

    def action_generate_va(self):
        config = self.env['bsi.api.config'].sudo().search([], limit=1)
        if not config:
            raise UserError("Konfigurasi API BSI belum diatur.")

        for invoice in self:
            payload = {
                "client_id": config.client_id,
                "trx_id": invoice.name,
                "trx_amount": invoice.amount_total,
                "customer_name": invoice.santri_id.name,
                "customer_email": invoice.santri_id.email,
                "customer_phone": invoice.santri_id.phone,
                "datetime_expired": (fields.Datetime.now() + relativedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"Tagihan untuk {invoice.santri_id.name}",
                "type": "createbilling"
            }

            try:
                encrypted_data = BSIEncryption.encrypt(payload, config.client_id, config.secret_key)
                data = {
                    "client_id": config.client_id,
                    "data": encrypted_data
                }

                url = config.base_url.rstrip("/") + "/ext/bnis/?fungsi=vabilling"
                headers = {"Content-Type": "application/json"}

                response = requests.post(url, json=data, headers=headers, timeout=10)
                _logger.info("Response BSI: %s", response.text)

                if response.status_code != 200:
                    raise UserError(f"Gagal buat VA: Status {response.status_code} dari server BSI")

                try:
                    res_data = response.json()
                except json.JSONDecodeError:
                    raise UserError("Gagal parsing response dari BSI. Format tidak valid JSON.")

                if res_data.get("status") != "000":
                    raise UserError(f"Gagal buat VA: {res_data.get('status_msg', 'Unknown Error')}")

                if "data" not in res_data:
                    raise UserError("Gagal buat VA: Data tidak ditemukan di response.")

                decrypted = BSIEncryption.decrypt(res_data["data"], config.client_id, config.secret_key)

                invoice.va_number = decrypted.get("virtual_account")
                invoice.state = "unpaid"

            except requests.exceptions.RequestException as e:
                _logger.exception("Koneksi ke API BSI gagal:")
                raise UserError(f"Gagal menghubungi API BSI: {str(e)}")

            except Exception as e:
                _logger.exception("Gagal buat VA karena error tak terduga:")
                raise UserError(f"Gagal buat VA: {str(e)}")


    def action_update_va(self):
        config = self.env['bsi.api.config'].sudo().search([], limit=1)
        if not config:
            raise UserError("Konfigurasi API BSI belum diatur.")

        for invoice in self:
            if not invoice.va_number:
                raise UserError("Invoice belum memiliki Virtual Account.")

            payload = {
                "client_id": config.client_id,
                "trx_id": invoice.name,
                "trx_amount": invoice.amount_total,
                "customer_name": invoice.santri_id.name,
                "datetime_expired": (fields.Datetime.now() + relativedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "virtual_account": invoice.va_number,
                "description": f"Update tagihan untuk {invoice.santri_id.name}",
                "type": "updatebilling"
            }

            encrypted_data = BSIEncryption.encrypt(payload, config.client_id, config.secret_key)

            data = {
                "client_id": config.client_id,
                "data": encrypted_data
            }

            url = config.base_url.rstrip("/") + "/ext/bnis/?fungsi=vabilling"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=data, headers=headers)
            if not response.ok:
                raise UserError(f"Request Gagal: {response.text}")

            res_data = response.json()
            if res_data.get("status") != "000":
                raise UserError(f"Gagal update VA: {res_data.get('status_msg', 'Unknown Error')}")

    def action_inquiry_va(self):
        config = self.env['bsi.api.config'].sudo().search([], limit=1)
        if not config:
            raise UserError("Konfigurasi API BSI belum diatur.")

        for invoice in self:
            if not invoice.name:
                raise UserError("Invoice belum memiliki nomor transaksi (trx_id).")

            try:
                payload = {
                    "client_id": config.client_id,
                    "trx_id": invoice.name,
                    "type": "inquirybilling",
                }

                _logger.info("Payload asli inquiry VA: %s", payload)

                encrypted_data = BSIEncryption.encrypt(
                    payload,
                    config.client_id,
                    config.secret_key
                )

                request_payload = {
                    "client_id": config.client_id,
                    "data": encrypted_data,
                }

                url = config.base_url.rstrip("/") + "/ext/bnis/?fungsi=vabilling"
                headers = {
                    "Content-Type": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Accept-Language": "en-US,en;q=0.8,id;q=0.6",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Odoo Integration)",
                }

                response = requests.post(url, json=request_payload, headers=headers, timeout=10)
                _logger.info("Response Inquiry BSI: %s", response.text)

                if response.status_code != 200:
                    raise UserError(f"Gagal inquiry VA: Status {response.status_code} dari server BSI")

                res_data = response.json()
                if res_data.get("status") != "000":
                    raise UserError(f"Gagal inquiry VA: {res_data.get('status_msg', 'Unknown Error')}")

                decrypted = BSIEncryption.decrypt(res_data["data"], config.client_id, config.secret_key)

                # Tampilkan info hasil ke chatter (jika ingin)
                invoice.message_post(body=f"Inquiry berhasil:<br/><pre>{json.dumps(decrypted, indent=2)}</pre>")

            except requests.exceptions.RequestException as e:
                _logger.exception("Gagal koneksi ke API BSI (Inquiry):")
                raise UserError(f"Gagal terhubung ke API BSI: {str(e)}")
            except Exception as e:
                _logger.exception("Error tidak terduga saat proses inquiry VA:")
                raise UserError(f"Error tidak terduga: {str(e)}")



