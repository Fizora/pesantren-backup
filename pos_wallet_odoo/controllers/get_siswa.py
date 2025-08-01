# from odoo import http
# from odoo.http import request
# from odoo.exceptions import ValidationError

# class SiswaController(http.Controller):

#     @http.route('/siswa/get_data', type='json', auth='user')
#     def get_data(self, domain=None):
#         """
#         Mengambil data dari model `res.partner` dengan filter domain opsional.
        
#         :param domain: List berisi filter domain Odoo untuk memfilter data siswa (opsional).
#         :return: List berisi data siswa sesuai filter yang diberikan.
#         """
#         try:
#             # Jika tidak ada domain, gunakan list kosong agar semua data diambil
#             domain = domain or []

#             # Jika domain diberikan, batasi hasil pencarian menjadi satu data
#             limit = 1 if domain else None

#             # Cari data sesuai domain yang diberikan dengan limit jika diperlukan
#             siswa_records = request.env['res.partner'].sudo().search(domain, limit=limit)

#             data = [{
#                 'partner_id': record.id,
#                 'name': record.name,
#                 'nis': record.nis,
#                 'wallet_balance': record.wallet_balance,
#                 'pin': record.wallet_pin,
#             } for record in siswa_records]

#             return data
#         except Exception as e:
#             return {'error': str(e)}

#     # @http.route('/siswa/deduct_wallet', type='json', auth='user')
#     # def deduct_wallet(self, partner_id, amount):
#     #     """
#     #     Mengurangi wallet_balance pada partner yang diberikan dengan amount tertentu.
        
#     #     :param partner_id: ID dari partner (siswa) yang wallet_balance-nya akan dikurangi.
#     #     :param amount: Jumlah yang akan dikurangi dari wallet_balance.
#     #     :return: Status sukses atau error.
#     #     """
#     #     try:
#     #         # Validasi amount harus positif
#     #         if amount <= 0:
#     #             raise ValidationError("Jumlah yang dikurangi harus lebih besar dari nol.")
            
#     #         # Cari partner berdasarkan ID
#     #         partner = request.env['res.partner'].sudo().browse(partner_id)
#     #         partnerTransaksi = request.env['pos.wallet.transaction'].sudo().browse(partner_id)

#     #         transaksi_terbaru = request.env['pos.wallet.transaction'].search([
#     #             ('partner_id', '=', partnerTransaksi)
#     #         ],order="create_date desc", limit=1)
            
#     #         # Validasi jika partner ditemukan
#     #         if not partner.exists():
#     #             raise ValidationError("Siswa dengan ID tersebut tidak ditemukan.")
            
#     #         # Validasi jika saldo mencukupi
#     #         if partner.wallet_balance < amount:
#     #             raise ValidationError("Saldo tidak mencukupi untuk melakukan pengurangan.")

#     #         # Kurangi saldo
#     #         partner.sudo().write({'wallet_balance': partner.wallet_balance - amount})
#     #         partnerTransaksi.sudo().write({
#     #             'amount': transaksi_terbaru.amount - amount
#     #         })

#     #         return {'success': True, 'new_balance': partner.wallet_balance}
#     #     except ValidationError as e:
#     #         return {'error': str(e)}
#     #     except Exception as e:
#     #         return {'error': 'Terjadi kesalahan: ' + str(e)}

    
    
#     @http.route('/siswa/deduct_wallet', type='json', auth='user')
#     def deduct_wallet(self, partner_id, amount):
#         """
#         Mengurangi wallet_balance pada partner yang diberikan dengan amount tertentu.
            
#         :param partner_id: ID dari partner (siswa) yang wallet_balance-nya akan dikurangi.
#         :param amount: Jumlah yang akan dikurangi dari wallet_balance.
#         :return: Status sukses atau error.
#         """
#         try:
#             # Validasi amount harus positif
#             if amount <= 0:
#                 raise ValidationError("Jumlah yang dikurangi harus lebih besar dari nol.")
                
#             # Cari partner berdasarkan ID
#             partner = request.env['res.partner'].sudo().browse(partner_id)
            
#             # Validasi jika partner ditemukan
#             if not partner.exists():
#                 raise ValidationError("Siswa dengan ID tersebut tidak ditemukan.")
                
#             # Validasi jika saldo mencukupi
#             if partner.wallet_balance < amount:
#                 raise ValidationError("Saldo tidak mencukupi untuk melakukan pengurangan.")
            
#             # Cari transaksi terbaru untuk partner ini
#             transaksi_terbaru = request.env['pos.wallet.transaction'].search([
#                 ('partner_id', '=', partner_id)  # Gunakan partner_id, bukan objek
#             ], order="create_date desc", limit=1)
            
#             # Kurangi saldo
#             partner.sudo().write({'wallet_balance': partner.wallet_balance - amount})
            
#             # Update juga transaksi terbaru jika ditemukan
#             if transaksi_terbaru:
#                 transaksi_terbaru.sudo().write({
#                     'amount': transaksi_terbaru.amount - amount
#                 })
            
#             return {'success': True, 'new_balance': partner.wallet_balance}
#         except ValidationError as e:
#             return {'error': str(e)}
#         except Exception as e:
#             return {'error': 'Terjadi kesalahan: ' + str(e)}

#     @http.route('/siswa/get_data/bar', type='json', auth='user')
#     def get_data_bar(self, barcode=None):
#         """
#         Mengambil data dari model `res.partner` berdasarkan barcode.
        
#         :param barcode: String berisi barcode untuk memfilter data siswa (opsional).
#         :return: Dictionary berisi data siswa sesuai barcode yang diberikan.
#         """
#         try:
#             # Jika barcode tidak diberikan, kembalikan error
#             if not barcode:
#                 return #{'error': 'Barcode tidak diberikan'}

#             # Cari data siswa berdasarkan barcode
#             siswa_record = request.env['res.partner'].sudo().search([('barcode', '=', barcode)], limit=1)

#             # Jika tidak ditemukan, kembalikan pesan error
#             if not siswa_record:
#                 return #{'error': 'Data siswa tidak ditemukan'}

#             data = {
#                 'partner_id': siswa_record.id,
#                 'name': siswa_record.name,
#                 'nis': siswa_record.nis,
#                 'wallet_balance': siswa_record.wallet_balance,
#                 'pin': siswa_record.wallet_pin,
#             }

#             return data
#         except Exception as e:
#             # raise ValidationError(f"Error fetching data for barcode {barcode}: {str(e)}")
#             return #{'error': str(e)}




from odoo import http,fields
from odoo.http import request
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
import json
import requests
import base64


_logger = logging.getLogger(__name__)

class SiswaController(http.Controller):

    @http.route('/siswa/get_data', type='json', auth='user')
    def get_data(self, domain=None):
        """
        Mengambil data dari model `res.partner` dengan filter domain opsional.
        
        :param domain: List berisi filter domain Odoo untuk memfilter data siswa (opsional).
        :return: List berisi data siswa sesuai filter yang diberikan.
        """
        try:
            # Jika tidak ada domain, gunakan list kosong agar semua data diambil
            domain = domain or []

            # Jika domain diberikan, batasi hasil pencarian menjadi satu data
            limit = 1 if domain else None

            # Cari data sesuai domain yang diberikan dengan limit jika diperlukan
            siswa_records = request.env['res.partner'].sudo().search(domain, limit=limit)

            data = [{
                'partner_id': record.id,
                'name': record.name,
                'nis': record.nis,
                'saldo_uang_saku': record.saldo_uang_saku,
                'pin': record.wallet_pin,
            } for record in siswa_records]

            return data
        except Exception as e:
            return {'error': str(e)}
    
    @http.route('/siswa/deduct_wallet', type='json', auth='user')
    def deduct_wallet(self, partner_id, amount, order_details=None):
        """
        Mengurangi wallet_balance pada partner yang diberikan dengan amount tertentu.
            
        :param partner_id: ID dari partner (siswa) yang wallet_balance-nya akan dikurangi.
        :param amount: Jumlah yang akan dikurangi dari wallet_balance.
        :return: Status sukses atau error.
        """
        try:
            if amount <= 0:
                raise ValidationError("Jumlah yang dikurangi harus lebih besar dari nol.")
                
            # Cari partner berdasarkan ID
            partner = request.env['res.partner'].sudo().browse(partner_id)
            santri = request.env['cdn.siswa'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            timestamp = fields.Datetime.now()

            santri = request.env['cdn.siswa'].sudo().search([('partner_id', '=', partner_id)], limit=1)

            if santri.status_akun in ['nonaktif', 'blokir']:
                return {'error': "Pembayaran ini tidak dapat diproses karena statusnya sedang tidak aktif atau telah diblokir. Silakan hubungi pihak pengurus pesantren untuk informasi lebih lanjut."}
        
            if santri and santri.is_limit_active:
                now = fields.Datetime.now()
                if santri.limit_reset_date and now >= santri.limit_reset_date:
                    reset_date = now

                    if santri.limit == 'hari':
                        reset_date = now + relativedelta(days=1)
                    elif santri.limit == 'minggu':
                        reset_date = now + relativedelta(weeks=1)
                    elif santri.limit == 'bulan':
                        reset_date = now + relativedelta(months=1)
                          
                    santri.write({
                        'used_amount': 0,
                        'limit_reset_date': reset_date
                    })

                remaining = santri.amount - santri.used_amount
                if amount > remaining:
                    nama_santri = santri.name
                    reset_date  = santri.limit_reset_date
                    limit_option = santri.limit
                    limit_periode = {
                        'hari': 'Harian',
                        'minggu': 'Mingguan',
                        'bulan': 'Bulanan'
                    }.get(limit_option, 'Tidak Diketahui')

                    now = fields.Datetime.now()
                    delta = reset_date - now
                    if delta.total_seconds() > 0:
                        days = delta.days
                        hours, remainder = divmod(delta.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        waktu_tunggu = f"{days} hari, {hours} jam, {minutes} menit"
                    else:
                        waktu_tunggu = "sebentar lagi"

                    return {
                        'warning' : True,
                        'message': f"Santri bernama {nama_santri} telah mencapai batas penggunaan saldo {limit_periode}, coba lagi setelah {waktu_tunggu}"
                    }

                santri.write({
                    'used_amount': santri.used_amount + amount
                })

            
            # Validasi jika partner ditemukan
            if not partner.exists():
                raise ValidationError("Siswa dengan ID tersebut tidak ditemukan.")
                
            # Validasi jika saldo mencukupi
            if partner.saldo_uang_saku < amount:
                raise ValidationError("Saldo tidak mencukupi untuk melakukan pengurangan.")
            
            nama_santri = santri.name or "Santri"

            keterangan = self._generate_transaction_description(order_details, amount, santri_name=nama_santri)

            transaksi_terbaru = request.env['pos.wallet.transaction'].search([
                ('partner_id', '=', partner_id)
            ], order="create_date desc", limit=1)

            # transaksi_saldo_saku = request.env['cdn_uang_saku'].search([
            #     ('partner_id', '=', partner_id)
            # ], order="create_date desc", limit=1)
            
            partner.sudo().write({'saldo_uang_saku': partner.saldo_uang_saku - amount})

            request.env['cdn.uang_saku'].sudo().create({
                'tgl_transaksi': timestamp,
                'siswa_id': partner.id,
                'jns_transaksi': 'keluar',
                'amount_out': amount,
                'validasi_id': request.env.user.id,
                'validasi_time': timestamp,
                'keterangan': keterangan,
                'state': 'confirm',
            })

            if transaksi_terbaru:
                transaksi_terbaru.sudo().write({
                    'amount': transaksi_terbaru.amount - amount
                })
            
            return {'success': True, 'new_balance': partner.saldo_uang_saku}
        except ValidationError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': 'Terjadi kesalahan: ' + str(e)}

    def _generate_transaction_description(self, order_details, amount, santri_name="Santri"):
        """
        Generate deskripsi transaksi pendek, cocok untuk dashboard.
        Contoh hasil: "Transaksi POS atas nama Ahmad: Pembelian 2x Nasi Goreng, 1x Nasi Pecel. Total Rp 30.000"
        """
        try:
            total_amount = order_details.get('total_amount', amount) if order_details else amount
            items = order_details.get('items', []) if order_details else []

            # Susun deskripsi item maksimal 3 biar pendek
            product_lines = []
            for item in items[:3]:
                product_name = item.get('product_name', 'Produk')
                qty = item.get('quantity', 0)
                product_lines.append(f"{qty}x {product_name}")
            if len(items) > 3:
                product_lines.append("dll.")

            return f"Transaksi POS atas nama {santri_name}: Pembelian {', '.join(product_lines)}. Total Rp {total_amount:,.0f}"
        except Exception as e:
            return f"Transaksi POS - Total: Rp {amount:,.0f} (Error: {str(e)})"


    @http.route('/siswa/get_data/bar', type='json', auth='user')
    def get_data_bar(self, barcode=None):
        """
        Mengambil data dari model `res.partner` berdasarkan barcode.
        
        :param barcode: String berisi barcode untuk memfilter data siswa (opsional).
        :return: Dictionary berisi data siswa sesuai barcode yang diberikan.
        """
        try:
            # Jika barcode tidak diberikan, kembalikan None
            if not barcode:
                return None

            # Cari data siswa berdasarkan barcode
            siswa_record = request.env['res.partner'].sudo().search([('barcode', '=', barcode)], limit=1)

            # Jika tidak ditemukan, kembalikan None
            if not siswa_record:
                return None

            data = {
                'partner_id': siswa_record.id,
                'name': siswa_record.name,
                'nis': siswa_record.nis,
                'wallet_balance': siswa_record.saldo_uang_saku,
                'pin': siswa_record.wallet_pin,
            }

            return data
        except Exception as e:
            _logger.error(f"Error fetching data for barcode {barcode}: {str(e)}")
            return None

    @http.route('/siswa/search', type='json', auth='user')
    def search_siswa(self, query=None, no_limit=False, **kw):
        """
        Mencari data siswa berdasarkan query pencariannya.
        
        :param query: String berisi kata kunci pencarian.
        :param no_limit: Boolean yang menentukan apakah ada batasan jumlah hasil atau tidak.
        :return: Dictionary berisi list data siswa yang cocok dengan pencarian.
        """
        if not query:
            return {'partners': []}
        
        # Tentukan limit berdasarkan parameter no_limit
        limit = None if no_limit else 100  # Default 100 jika no_limit tidak diaktifkan
        
        # Cari di database lokal Odoo
        local_partners = request.env['res.partner'].search([
            '|', '|', '|',
            ('name', 'ilike', query),
            ('barcode', 'ilike', query),
            ('nis', 'ilike', query),
            ('phone', 'ilike', query)
        ], limit=limit)
        
        partners_list = local_partners.read(['id', 'name', 'barcode', 'nis', 'saldo_uang_saku', 'street', 'email', 'phone'])
        
        # Format wallet_balance untuk tampilan
        for partner in partners_list:
            if 'saldo_uang_saku' in partner:
                partner['wallet_balance_display'] = f"Rp {partner['saldo_uang_saku']:,.0f}"
        
        # Return combined results
        return {
            'partners': partners_list
        }

    @http.route('/pos/midtrans/create_transaction', type='json', auth='user', methods=['POST'])
    def create_midtrans_transaction(self, **kwargs):
        try:
            order_data = kwargs.get('order_data')
            
            server_key = 'SB-Mid-server-0wpmMgUXsngOJfivQ_vRW4nM'
            is_production = False
            
            if not server_key:
                return {
                    'success': False,
                    'error': 'Midtrans server key not configured'
                }
            
            # Midtrans API URL
            if is_production:
                api_url = 'https://app.midtrans.com/snap/v1/transactions'
            else:
                api_url = 'https://app.sandbox.midtrans.com/snap/v1/transactions'
            
            # Prepare headers
            auth_string = f"{server_key}:"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_b64}'
            }
            
            # Make request to Midtrans
            response = requests.post(api_url, json=order_data, headers=headers)
            response_data = response.json()
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'snap_token': response_data.get('token'),
                    'redirect_url': response_data.get('redirect_url')
                }
            else:
                _logger.error(f"Midtrans API error: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('error_messages', ['Unknown error'])[0] if response_data.get('error_messages') else 'API request failed'
                }
                
        except Exception as e:
            _logger.error(f"Error creating Midtrans transaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/pos/midtrans/verify_payment', type='json', auth='user', methods=['POST'])
    def verify_midtrans_payment(self, **kwargs):
        try:
            transaction_id = kwargs.get('transaction_id')
            order_id = kwargs.get('order_id')
            
            if not transaction_id:
                return {
                    'success': False,
                    'error': 'Transaction ID is required'
                }

            server_key = 'SB-Mid-server-0wpmMgUXsngOJfivQ_vRW4nM'
            is_production = False
            
            if not server_key:
                return {
                    'success': False,
                    'error': 'Midtrans server key not configured'
                }
            
            # Midtrans API URL for status check
            if is_production:
                api_url = f'https://api.midtrans.com/v2/{order_id}/status'
            else:
                api_url = f'https://api.sandbox.midtrans.com/v2/{order_id}/status'
            
            # Prepare headers
            auth_string = f"{server_key}:"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_b64}'
            }
            
            # Make request to Midtrans
            response = requests.get(api_url, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200:
                transaction_status = response_data.get('transaction_status')
                fraud_status = response_data.get('fraud_status')
                
                # Check if payment is successful
                is_success = (
                    transaction_status in ['capture', 'settlement'] and
                    fraud_status in ['accept', None]
                ) or transaction_status == 'settlement'
                
                return {
                    'success': is_success,
                    'transaction_status': transaction_status,
                    'fraud_status': fraud_status,
                    'payment_type': response_data.get('payment_type'),
                    'gross_amount': response_data.get('gross_amount'),
                    'transaction_time': response_data.get('transaction_time'),
                    'data': response_data
                }
            else:
                _logger.error(f"Midtrans verification error: {response_data}")
                return {
                    'success': False,
                    'error': 'Failed to verify payment status'
                }
                
        except Exception as e:
            _logger.error(f"Error verifying Midtrans payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/pos/midtrans/notification', type='http', auth='public', methods=['POST'], csrf=False)
    def midtrans_notification(self, **kwargs):
        """
        Handle Midtrans notification/webhook
        """
        try:
            notification_data = json.loads(request.httprequest.data.decode('utf-8'))
            
            order_id = notification_data.get('order_id')
            transaction_status = notification_data.get('transaction_status')
            fraud_status = notification_data.get('fraud_status')
            
            _logger.info(f"Midtrans notification received for order {order_id}: {transaction_status}")
            
            # Process the notification based on transaction status
            if transaction_status == 'settlement':
                # Payment successful
                self._handle_successful_payment(notification_data)
            elif transaction_status in ['cancel', 'deny', 'expire']:
                # Payment failed/cancelled
                self._handle_failed_payment(notification_data)
            elif transaction_status == 'pending':
                # Payment pending
                self._handle_pending_payment(notification_data)
            
            return request.make_response('OK', headers=[('Content-Type', 'text/plain')])
            
        except Exception as e:
            _logger.error(f"Error processing Midtrans notification: {str(e)}")
            return request.make_response('Error', status=500)
    
    def _handle_successful_payment(self, notification_data):
        """Handle successful payment notification"""
        try:
            order_id = notification_data.get('order_id')
            # Add logic to update order status in database if needed
            _logger.info(f"Payment successful for order {order_id}")
        except Exception as e:
            _logger.error(f"Error handling successful payment: {str(e)}")
    
    def _handle_failed_payment(self, notification_data):
        """Handle failed payment notification"""
        try:
            order_id = notification_data.get('order_id')
            # Add logic to handle failed payment
            _logger.info(f"Payment failed for order {order_id}")
        except Exception as e:
            _logger.error(f"Error handling failed payment: {str(e)}")
    
    def _handle_pending_payment(self, notification_data):
        """Handle pending payment notification"""
        try:
            order_id = notification_data.get('order_id')
            # Add logic to handle pending payment
            _logger.info(f"Payment pending for order {order_id}")
        except Exception as e:
            _logger.error(f"Error handling pending payment: {str(e)}")

