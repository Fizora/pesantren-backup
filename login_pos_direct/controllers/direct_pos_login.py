from odoo import http
from odoo.http import request
import werkzeug
from odoo.addons.web.controllers import home
from odoo.exceptions import UserError

class PosScreen(home.Home):
    """The class PosScreen is used to log in pos session directly"""
   
    @http.route('/web/login', type='http', auth="public", website=True, sitemap=False)
    def web_login(self, redirect=None, **kw):
        """Override to add direct login to POS"""
        # Panggil method login asli dari parent class
        res = super(PosScreen, self).web_login(redirect=redirect, **kw)
       
        # Periksa apakah pengguna memiliki konfigurasi POS
        if request.env.user.pos_conf_id:
            try:
                # Cari sesi POS yang sudah terbuka
                existing_sessions = request.env['pos.session'].sudo().search([
                    ('user_id', '=', request.env.uid),
                    ('state', '=', 'opened'),
                    ('config_id', '=', request.env.user.pos_conf_id.id)
                ])
                
                # Tutup sesi yang sudah terbuka sebelumnya
                if existing_sessions:
                    for session in existing_sessions:
                        try:
                            session.action_pos_session_closing_control()
                        except Exception:
                            session.state = 'closed'
                
                # Buat sesi baru
                new_session = request.env['pos.session'].sudo().create({
                    'user_id': request.env.uid,
                    'config_id': request.env.user.pos_conf_id.id,
                    'state': 'opened'
                })
                
                # Redirect ke halaman POS
                return werkzeug.utils.redirect(f'/pos/ui?config_id={new_session.config_id.id}')
            
            except Exception as e:
                # Tangani kesalahan yang mungkin terjadi
                return request.render('web.login', {
                    'error': str(e)
                })
       
        # Kembalikan respons default jika tidak ada konfigurasi POS
        return res



# from odoo import http
# from odoo.http import request
# import werkzeug
# from odoo.addons.web.controllers import home
# from odoo.exceptions import UserError

# class PosScreen(home.Home):
#     """Kelas PosScreen digunakan untuk login langsung ke sesi POS"""
   
#     @http.route('/web/login', type='http', auth="public", website=True, sitemap=False)
#     def web_login(self, redirect=None, **kw):
#         """Override untuk menambahkan login langsung ke POS"""
#         # Panggil metode login asli dari kelas induk
#         res = super(PosScreen, self).web_login(redirect=redirect, **kw)
       
#         # Periksa apakah pengguna memiliki konfigurasi POS
#         if request.env.user.pos_conf_id:
#             try:
#                 # Cari sesi POS yang sudah terbuka untuk pengguna dan konfigurasi ini
#                 existing_sessions = request.env['pos.session'].sudo().search([
#                     ('user_id', '=', request.env.uid),
#                     ('state', '=', 'opened'),
#                     ('config_id', '=', request.env.user.pos_conf_id.id)
#                 ])
                
#                 # Tutup sesi yang sudah terbuka sebelumnya
#                 for session in existing_sessions:
#                     try:
#                         session.action_pos_session_closing_control()
#                     except Exception:
#                         session.state = 'closed'
                
#                 # Buat sesi POS baru
#                 new_session = request.env['pos.session'].sudo().create({
#                     'user_id': request.env.uid,
#                     'config_id': request.env.user.pos_conf_id.id,
#                     'state': 'opened'
#                 })
                
#                 # Arahkan ke halaman POS UI dengan ID konfigurasi sesi baru
#                 return werkzeug.utils.redirect(f'/pos/ui?config_id={new_session.config_id.id}')
            
#             except Exception as e:
#                 # Tangani kesalahan yang mungkin terjadi
#                 return request.render('web.login', {
#                     'error': str(e)
#                 })
       
#         # Kembalikan respons default jika tidak ada konfigurasi POS
#         return res

#     @http.route('/web', type='http', auth="user")
#     def web_client(self, s_action=None, **kw):
#         """Override untuk mengarahkan pengguna POS ke POS UI saat mengakses /web"""
#         # Periksa apakah pengguna memiliki konfigurasi POS
#         if request.env.user.pos_conf_id:
#             # Arahkan ke POS UI dengan ID konfigurasi pengguna
#             return werkzeug.utils.redirect(f'/pos/ui?config_id={request.env.user.pos_conf_id.id}')
#         # Jika tidak, lanjutkan dengan perilaku default
#         return super(PosScreen, self).web_client(s_action=s_action, **kw)



