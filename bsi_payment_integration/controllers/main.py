from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from ..utils.bsi_encryption import BSIEncryption
import json
import logging

_logger = logging.getLogger(__name__)

class BsiPaymentCallbackController(http.Controller):

    @http.route('/bsi/payment_callback', type='json', auth='public', csrf=False)
    def bsi_payment_callback(self, **kwargs):
        try:
            client_id = kwargs.get("client_id")
            encrypted_data = kwargs.get("data")
            _logger.info(f"Callback diterima: client_id={client_id}")

            if not client_id or not encrypted_data:
                return {"status": "error", "message": "Missing client_id or data"}

            config = request.env['bsi.api.config'].sudo().search([("client_id", "=", client_id)], limit=1)
            if not config:
                return {"status": "error", "message": "Konfigurasi client_id tidak ditemukan."}

            # Decrypt data
            try:
                decrypted = BSIEncryption.decrypt(encrypted_data, config.client_id, config.secret_key)
            except Exception as e:
                _logger.error(f"Error decrypt data: {e}")
                return {"status": "error", "message": "Gagal dekripsi data"}

            trx_id = decrypted.get("trx_id")
            va_number = decrypted.get("virtual_account")
            amount = decrypted.get("trx_amount")
            status = decrypted.get("payment_status")

            invoice = request.env["account.move"].sudo().search([("name", "=", trx_id)], limit=1)
            if not invoice:
                return {"status": "error", "message": "Invoice tidak ditemukan."}

            # Mark invoice as paid
            invoice.payment_state = "paid"

            # Log payment
            request.env["bsi.payment.log"].sudo().create({
                "transaction_id": trx_id,
                "va_number": va_number,
                "amount": amount,
                "status": status,
                "invoice_id": invoice.id,
                "raw_payload": json.dumps(decrypted, indent=2),
                "note": "Pembayaran diterima dari BSI callback",
            })

            return {"status": "success", "message": "Pembayaran berhasil diproses"}

        except Exception as e:
            _logger.exception("Error processing BSI callback")
            return {"status": "error", "message": f"Exception: {str(e)}"}
