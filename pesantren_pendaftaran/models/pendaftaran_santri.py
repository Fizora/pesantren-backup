from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError, UserError
import uuid
from datetime import datetime, timedelta
from odoo.tools import format_date
import pytz
import random
import string
import logging

_logger = logging.getLogger()
 
class ResPartner(models.Model):
    _inherit            = 'res.partner'

    virtual_account     = fields.Char(string='Virtual Account', store=True)
    va_saku             = fields.Char(string='No. VA Uang Saku', store=True)
    bank                = fields.Many2one('ubig.bank', string="PPilih Bank untuk VA", help="Pilih bank untuk membuat virtual account")
    petunjuk_pembayaran = fields.Text(related='bank.petunjuk_pembayaran', string="Petunjuk Pembayaran")
    jns_partner         = fields.Selection(string='Jenis Partner', selection=[
                        ('siswa', 'Siswa'), 
                        ('ortu', 'Orang Tua'), 
                        ('guru', 'Guru'), 
                        ('umum', 'Umum'), 
                        ('calon_santri', 'Calon Santri')]
                        , default="calon_santri", readonly="true")

class DataPendaftaran(models.Model):
    _name               = 'ubig.pendaftaran'
    _inherit            = ['mail.thread', 'mail.activity.mixin']
    _inherits           = {"res.partner": "partner_id"}
    _description        = 'Data Pendaftaran'
    _order              = 'tanggal_daftar desc, total_nilai desc'
    

    token = fields.Char(string='Token')
    is_notified = fields.Boolean(string='Notif', default=False)
    nomor_pendaftaran   = fields.Char(string='No Pendaftaran',readonly=True)
    tanggal_daftar      = fields.Date(string='Tanggal Daftar', default=fields.Date.context_today)
    partner_id          = fields.Many2one('res.partner', string="Nama Santri", required=False, help="Nama Calon Santri")
    siswa_id            = fields.Many2one('cdn.siswa',ondelete='cascade' ,string="Data Siswa", readonly=True)
    # Username 
    nik                 = fields.Char(string="NIK", help="Nomor Induk Keluarga Calon santri")
    email               = fields.Char(string="email", help="Email Calon Santri")
    password            = fields.Char(string="Kata Sandi", help="Kata Sandi Login")
    nomor_hp            = fields.Char(string="Nomor HP", help="Nomor HP/WhatsApp Calon Santri")
    nomor_login         = fields.Char(string="Nomor HP", help="Nomor HP/WhatsApp Untuk Login")
  
    # Jenjang Calon Santri
    jenjang_id          = fields.Many2one('ubig.pendidikan', string="Jenjang Pendidikan")
    jenjang             = fields.Selection(related='jenjang_id.jenjang', string='Jenjang', readonly=True)

    ini_nama            = fields.Char(related="jenjang_id.name", string="ya hoo")

    biaya               = fields.Integer(related='jenjang_id.biaya', string='Biaya Pendaftaran', readonly=True)
    keterangan          = fields.Char(related='jenjang_id.keterangan', string='Keterangan', readonly=True)

    # Data Diri
    gender              = fields.Selection([('L','Laki - Laki'),('P','Perempuan'),], string="Jenis Kelamin")
    kota_lahir          = fields.Char(string="Kota Kelahiran")
    tanggal_lahir       = fields.Date(string="Tanggal Lahir")
    golongan_darah      = fields.Selection([
                        ('A', 'A'),
                        ('B', 'B'),
                        ('AB', 'AB'),
                        ('O', 'O'),
                        ], string="Golongan Darah")
    kewarganegaraan     = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Kewarganegaraan",  help="")
    alamat              = fields.Char(string='Alamat')
    provinsi_id         = fields.Many2one(comodel_name="cdn.ref_propinsi",  string="Provinsi",  help="")
    kota_id             = fields.Many2one(comodel_name="cdn.ref_kota",  string="Kota",  help="")
    kecamatan_id        = fields.Many2one(comodel_name="cdn.ref_kecamatan",  string="Kecamatan",  help="")
    nisn                = fields.Char(string="NISN")
    nis                 = fields.Char(string="NIS", store=True)
    anak_ke             = fields.Integer( string="Anak ke",  help="")
    jml_saudara_kandung = fields.Integer( string="Jml Saudara Kandung",  help="")
    cita_cita           = fields.Char(string='Cita-Cita')

    # Data Pendidikan
    asal_sekolah        = fields.Char(string='Asal Sekolah')
    alamat_asal_sek     = fields.Char(string='Alamat Sekolah Asal')
    telp_asal_sek       = fields.Char(string='No Telp Sekolah Asal')
    status_sekolah_asal = fields.Selection(string='Status Sekolah Asal', selection=[('swasta', 'Swasta'), ('negeri', 'Negeri'),])
    npsn                = fields.Char(string='NPSN Sekolah')

    # Data Orang Tua - Ayah
    nama_ayah           = fields.Char(string="Nama")
    ktp_ayah            = fields.Char(string="Nomor KTP")
    tanggal_lahir_ayah  = fields.Date(string="Tanggal Lahir")
    telepon_ayah        = fields.Char(string="Nomor Telepon")
    pekerjaan_ayah      = fields.Many2one('cdn.ref_pekerjaan',string="Pekerjaan")
    penghasilan_ayah    = fields.Selection([
                        ('1juta', ' < Rp. 1.000.000'),
                        ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
                        ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
                        ('11juta', '> Rp. 10.000.000')
                        ], string="Penghasilan")
    email_ayah          = fields.Char(string="Email", required=True)
    agama_ayah          = fields.Selection([
                        ('islam', 'Islam'),
                        ('kristen', 'Kristen'),
                        ('katolik', 'Katolik'),
                        ('hindu', 'Hindu'),
                        ('budha', 'Budha'),
                        ('lainnya', 'Lainnya'),
                        ], string="Agama")
    kewarganegaraan_ayah = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan")
    pendidikan_ayah     = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan")

    ayah_sdi            = fields.Selection([
                            ('sdi', 'SDI/DQI'),
                            ('bukan', 'Bukan SDI DfQI')
                        ],string="Sdi",default="bukan")

    ibu_sdi            = fields.Selection([
                            ('sdi', 'SDI/DQI'),
                            ('bukan', 'Bukan SDI DQI')
                        ],string="Sdi", default="bukan")

    # Data Orang Tua - Ibu
    nama_ibu            = fields.Char(string="Nama")
    ktp_ibu             = fields.Char(string="Nomor KTP")
    tanggal_lahir_ibu   = fields.Date(string="Tanggal Lahir")
    telepon_ibu         = fields.Char(string="Nomor Telepon")
    pekerjaan_ibu       = fields.Many2one('cdn.ref_pekerjaan', string="Pekerjaan")
    penghasilan_ibu     = fields.Selection([
                        ('1juta', ' < Rp. 1.000.000'),
                        ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
                        ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
                        ('11juta', '> Rp. 10.000.000')
                        ], string="Penghasilan")
    email_ibu           = fields.Char(string="Email", required=True)
    agama_ibu           = fields.Selection([
                        ('islam', 'Islam'),
                        ('kristen', 'Kristen'),
                        ('katolik', 'Katolik'),
                        ('hindu', 'Hindu'),
                        ('budha', 'Budha'),
                        ('lainnya', 'Lainnya'),
                        ], string="Agama")
    kewarganegaraan_ibu = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan")
    pendidikan_ibu      = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan")

    wali_nama           = fields.Char( string="Nama Wali",  help="")
    wali_tmp_lahir      = fields.Char( string="Tmp lahir (Wali)",  help="")
    wali_tgl_lahir      = fields.Date( string="Tgl lahir (Wali)",  help="")
    wali_telp           = fields.Char( string="No Telepon (Wali)",  help="")
    wali_email          = fields.Char( string="Email (Wali)",  help="")
    wali_password       = fields.Char( string="Password", help="")
    wali_agama          = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Wali)",  help="")
    wali_hubungan       = fields.Char( string="Hubungan dengan Siswa",  help="")

    # Dokumen Anak
    akta_kelahiran      = fields.Binary(string="Akta Kelahiran")
    kartu_keluarga      = fields.Binary(string="Kartu Keluarga")
    ijazah              = fields.Binary(string="Ijazah")
    surat_kesehatan     = fields.Binary(string="Surat Keterangan Sehat")
    pas_foto            = fields.Binary(string="Pas Foto Berwarna")
    skhun               = fields.Binary(string="SKHUN")
    raport_terakhir     = fields.Binary(string="Raport Terakhir")

    # Dokumen Orang Tua
    ktp_ortu            = fields.Binary(string="KTP Orang Tua/Wali")

    # Aspek Penilaian
    soal_ids            = fields.Many2many('seleksi.penilaian', string="Detail Penilaian")

    # Computed field untuk total nilai
    total_nilai         = fields.Integer(string="Total Nilai", compute="_compute_total_nilai", store=True)

    orangtua_id         = fields.Many2one('cdn.orangtua', string="Data Orang Tua", readonly=True)

    status_va           = fields.Selection([
                            ('temporary', 'Temporary'),
                            ('permanent', 'Permanent'),
                            ('inactive', 'Inactive'),
                        ], string="Status Virtual Account", default='temporary')

    # kode_akses          = fields.Char(string="Kode Akses")

    bukti_pembayaran = fields.Binary(string="Bukti Pembayaran")
    status_pembayaran = fields.Selection([
        ('belumbayar','Belum Bayar'),
        ('sudahbayar','Sudah Bayar')
        ], string="Status Pembayaran", default="belumbayar")

    # perubahan
    is_alumni = fields.Boolean(string='Alumni DQI', default=False)

    is_pindahan_sd = fields.Boolean(string='Pindahan SD', default=False)

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('terdaftar', 'Terdaftar'),
        ('seleksi', 'Seleksi'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
        ('batal', 'Batal'),
    ], string='Status', default='draft',
        track_visibility='onchange')

    show_password_button = fields.Boolean(compute='_compute_show_password_button')

    @api.depends('password')
    def _compute_show_password_button(self):
        for rec in self:
            rec.show_password_button = bool(rec.password)


    def action_show_password(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kata Sandi',
            'res_model': 'lihat.password.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_password': self.password,
            }
        }

    @api.depends('soal_ids')
    def _compute_total_nilai(self):
        for record in self:
            # Menghitung total nilai dari soal_ids
            record.total_nilai = sum(soal.nilai for soal in record.soal_ids if soal.nilai)

    

    @api.model
    def create(self, vals):
        """Membuat nomor pendaftaran otomatis dengan format YYYY0001 dan tetap mempertahankan virtual_account."""
        current_year = fields.Date.context_today(self).year % 100  # Ambil 2 digit terakhir dari tahun saat ini

        # Cari semua nomor_pendaftaran yang dimulai dengan current_year
        existing_records = self.search([('nomor_pendaftaran', 'ilike', f'{current_year}%')])

        # Tentukan nomor urut berikutnya
        last_numbers = [int(rec.nomor_pendaftaran[2:]) for rec in existing_records if rec.nomor_pendaftaran]
        next_number = max(last_numbers) + 1 if last_numbers else 1

        # Format nomor pendaftaran (contoh: 240001 untuk tahun 2024)
        vals['nomor_pendaftaran'] = f'{current_year}{str(next_number).zfill(4)}'
        _logger.info(f"Nomor Pendaftaran yang akan dibuat: {vals['nomor_pendaftaran']}")

        # Generate UUID token
        vals['token'] = str(uuid.uuid4())

        # Buat record
        record = super(DataPendaftaran, self).create(vals)
        _logger.info(f"Nomor Pendaftaran yang dibuat: {record.nomor_pendaftaran}")

        # Pastikan virtual_account tetap diproses jika dalam state 'draft'
        if record.state == 'draft' and not record.virtual_account:
            _logger.info(f"Generating virtual account for: {record.nomor_pendaftaran}")
            record.virtual_account = record._generate_virtual_account_temporary(record.nomor_pendaftaran)
            record.status_va = 'temporary'

        return record



    @api.model
    def _generate_nomor_pendaftaran(self):
        """Membuat nomor pendaftaran unik dengan format default jika tidak ada format tahun."""
        last_record = self.search([], order="nomor_pendaftaran desc", limit=1)

        if last_record and last_record.nomor_pendaftaran and last_record.nomor_pendaftaran.isdigit():
            last_number = int(last_record.nomor_pendaftaran[-3:]) + 1
        else:
            last_number = 1  # Jika tidak ada data, mulai dari 001
        
        new_nomor_pendaftaran = f"001{str(last_number).zfill(3)}"
        _logger.info(f"Nomor Pendaftaran Baru (Backup Format): {new_nomor_pendaftaran}")
        return new_nomor_pendaftaran

    def _generate_virtual_account_temporary(self, nomor_pendaftaran):
        """Membuat virtual account sementara berdasarkan nomor pendaftaran"""
        return f"VA{nomor_pendaftaran}{random.randint(1000, 9999)}"

    def _generate_nis(self):
        """Fungsi untuk membuat NIS otomatis"""
        if not self.nomor_pendaftaran or not self.tanggal_daftar:
            _logger.warning("NIS tidak bisa dibuat: Tanggal pendaftaran atau jenjang kosong.")
            return False

        # Mapping Kode Lembaga
        lembaga = {
            'paud': '01', 'tk': '02', 'sdmi': '03',
            'smpmts': '04', 'smama': '05', 'smk': '10', 'nonformal': '06'
        }.get(self.jenjang, '00')  # Default '00' jika tidak cocok

        # Konversi Tahun Daftar
        try:
            tahun_daftar = self.tanggal_daftar.strftime('%Y')[-2:]
        except AttributeError:
            tahun_daftar = '00'
 
        # Gunakan nomor_pendaftaran sebagai bagian dari NIS
        nomor = self.nomor_pendaftaran if self.nomor_pendaftaran and self.nomor_pendaftaran.isdigit() else "000"

        # Format NIS
        nis = f"{lembaga}.{tahun_daftar}.{nomor}"
        _logger.info(f"NIS yang dihasilkan: {nis}")  
        return nis
    
    @api.constrains('nis')
    def _check_nis(self):
        """Validasi NIS tidak boleh kosong dan minimal 8 karakter"""
        for record in self:
            if record.nis and len(record.nis) < 8:
                raise ValidationError("NIS harus memiliki minimal 8 karakter. Silakan periksa kembali.")    
    
    def hapus_pendaftaran_kadaluarsa(self):
        # Tentukan zona waktu Anda, misalnya 'Asia/Jakarta' untuk WIB
        timezone = pytz.timezone('Asia/Jakarta')
        for record in self:
            if record.tanggal_daftar:
                tgl_hari_ini = datetime.now(timezone).date()
                batas_waktu = record.tanggal_daftar + timedelta(days=7)

                # Debug
                # raise UserError(f"Tanggal setelah satu hari: {batas_waktu}, Tanggal hari ini: {tgl_hari_ini}")

                if tgl_hari_ini > batas_waktu:
                    pendaftaran_kadaluarsa = self.search([('state', '=', 'draft')])
                    pendaftaran_kadaluarsa.unlink()

    def action_terdaftar(self):
        self.state = 'terdaftar'

    def action_seleksi(self):
        self.state = 'seleksi'

    def action_diterima(self):
        nis = self._generate_nis()
        if nis:
            self.nis = nis  
        self.state = 'diterima'


    def action_ditolak(self):
        self.state = 'ditolak'

    def action_batal(self):
        self.state = 'batal'

    def action_draft(self):
        # Optional: You can define additional actions for when "Draft" is clicked
        self.write({'state': 'draft'})


    def action_report_pendaftaran(self):
        return self.env.ref('pesantren_pendaftaran.action_report_pendaftaran').report_action(self)

    # @api.model
    # def default_get(self, fields):
    # res = super(DataPendaftaran, self).default_get(fields)  # Use the exact class name here
    # res['jns_partner'] = 'calon_santri'
    # return res

    def write(self, vals):

        if 'status_pembayaran' in vals and vals['status_pembayaran'] == 'sudahbayar':
            self._create_journal_entry()

        if 'state' in vals and vals['state'] == 'diterima':
            for record in self:
                # Buat akun orang tua jika belum ada
                if not record.orangtua_id:
                    orangtua = record.create_orangtua()
                    record.orangtua_id = orangtua.id

                # Buat data siswa jika belum ada
                if not record.siswa_id:
                    siswa = record.create_siswa()
                    record.siswa_id = siswa.id

                # Buat data virtual account
                # if not record.virtual_account:
                #     nisn = record.nisn
                #     record.virtual_account = record._generate_virtual_account(nisn)
                nis = record.nis
                jenjang = record.jenjang
                # record.virtual_account = record._generate_virtual_account_permanent(nis, jenjang)
                record.status_va = 'permanent'

                # Buat data virtual account uang saku
                # if not record.va_saku:
                #     record.va_saku = record._generate_va_uangsaku(nis, jenjang)

                # Generate nis
                # if not record.nis:
                #     nisn = record.nisn
                #     record.nis = record._generate_nis(nisn)

        if 'state' in vals and vals['state'] == 'ditolak':
            for record in self:
                record.virtual_account = False # Menghapus Virtual Account
                record.status_va = 'inactive'

        # Check if state is being changed to 'terdaftar'
        # if 'state' in vals and vals['state'] == 'diterima':
        #     for record in self:
        #         if not record.virtual_account:
        #             record.virtual_account = "01" + record._generate_virtual_account()

        return super(DataPendaftaran, self).write(vals)
    
    def _create_journal_entry(self):
        """Mencatat jurnal secara otomatis."""
        for rec in self:
            if rec.status_pembayaran != 'sudahbayar':
                continue  # Lewati jika status bukan "sudah_bayar"

            # Ambil jurnal tipe "Cash"
            journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
            if not journal:
                raise ValidationError('Tidak ada jurnal tipe "Cash" yang ditemukan.')

            if not journal.default_account_id:
                raise ValidationError("Akun default tidak diatur untuk jurnal ini.")
            
            # Dapatkan akun debit dan kredit
            debit_account = journal.default_account_id
            credit_account = self.env['account.account'].search([('code', '=', '11110001')], limit=1)  # Sesuaikan dengan akun Anda

            if not credit_account:
                raise ValidationError("Akun kredit tidak ditemukan.")

            if not credit_account:
                raise ValidationError("Akun kredit tidak ditemukan.")


            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'date': fields.Date.today(),
                'line_ids': [
                    (0, 0, {
                        'account_id': debit_account.id,
                        'partner_id': self.partner_id.id if self.partner_id else False,
                        'name': 'Debit Entry',
                        'debit': self.biaya,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'account_id': credit_account.id,
                        'partner_id': self.partner_id.id if self.partner_id else False,
                        'name': 'Credit Entry',
                        'debit': 0.0,
                        'credit': self.biaya,
                    }),
                ],
            })
            move.action_post()
    
    # def create_orangtua(self):
    #     for record in self:
    #         """Fungsi untuk membuat akun orang tua di cdn.orangtua"""

    #         # Cek apakah email ayah sudah ada di res.partner
    #         existing_partner = self.env['res.partner'].search([('email', '=', record.email_ayah)], limit=1)
    #         existing_user = self.env['res.users'].search([('login', '=', record.email_ayah)], limit=1)

    #         if existing_partner:
    #             # Jika partner sudah ada, cek apakah data orang tua sudah ada
    #             existing_orangtua = self.env['cdn.orangtua'].sudo().search([('partner_id', '=', existing_partner.id)], limit=1)
    #             if existing_orangtua:
    #                 # Jika data orang tua sudah ada, gunakan data tersebut
    #                 return existing_orangtua
    #             else:
    #                 # Jika partner ada tapi data orang tua belum ada, buat data orang tua
    #                 orangtua_vals = {
    #                     'partner_id': existing_partner.id,
    #                     'hubungan': 'ayah',
    #                     'email': record.email_ayah,
    #                 }
    #                 orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)
    #                 return orangtua
    #         else:
    #             # Jika partner belum ada, buat data partner baru
    #             partner_vals = {
    #                 'name': record.nama_ayah,
    #                 'email': record.email_ayah,
    #                 'phone': record.telepon_ayah,
    #                 'city': record.kota_id.name,
    #             }
                
    #             # Membuat data partner untuk ayah
    #             partner = self.env['res.partner'].create(partner_vals)

    #             orangtua_vals = {
    #                 'partner_id': partner.id,
    #                 'hubungan': 'ayah',
    #                 'email': record.email_ayah,
    #             }
    #             orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)

    #             # Hanya buat user baru jika belum ada user dengan email yang sama
    #             if not existing_user:
    #                 # Generate password jika tidak ada
    #                 generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    
    #                 # Membuat user baru untuk ayah
    #                 user_vals = {
    #                     'login': record.email_ayah,
    #                     'partner_id': partner.id,
    #                     'password': generated_password,
    #                 }
    #                 new_user = self.env['res.users'].sudo().create(user_vals)
    #                 partner.user_id = new_user.id

    #                 # Kirim email informasi login
    #             email_values = {
    #                 'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
    #                 'email_to': record.email,
    #                 'body_html': f'''
    #                     <div style="background-color: #d9eaf7; padding: 20px; font-family: Arial, sans-serif;">
    #                         <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
    #                             <!-- Header -->
    #                             <div style="background-color: #0066cc; color: #ffffff; text-align: center; padding: 20px;">
    #                                 <h1 style="margin: 0; font-size: 24px;">Pesantren Daarul Qur'an Istiqomah</h1>
    #                             </div>
    #                             <!-- Body -->
    #                             <div style="padding: 20px; color: #555555;">
    #                                 <p style="margin: 0 0 10px;">Assalamualaikum Wr. Wb,</p>
    #                                 <p style="margin: 0 0 20px;">
    #                                     Bapak/Ibu <strong>{record.wali_nama or record.nama_ayah or record.nama_ibu}</strong>,<br>
    #                                     Akun Orang Tua telah dibuat di sistem pesantren kami. Berikut adalah informasi login Anda:
    #                                 </p>
    #                                 <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
    #                                     <table style="width: 100%; border-collapse: collapse;">
    #                                         <tr>
    #                                             <td style="padding: 8px; font-weight: bold; color: #333333;">Email</td>
    #                                             <td style="padding: 8px; color: #555555;">{record.email}</td>
    #                                         </tr>
    #                                     </table>
    #                                 </div>
    #                                 <p style="text-align: center;">
    #                                     <a href="/odoo" style="background-color: #0066cc; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
    #                                         Masuk Ke Akun Anda
    #                                     </a>
    #                                 </p>
    #                                 <p style="margin: 20px 0;">
    #                                     Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:
    #                                 </p>
    #                                 <ul style="margin: 0; padding-left: 20px; color: #555555;">
    #                                     <li>0822 5207 9785</li>
    #                                     <li>0853 9051 1124</li>
    #                                 </ul>
    #                                 <p style="margin: 20px 0;">
    #                                     Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.
    #                                 </p>
    #                             </div>
    #                             <!-- Footer -->
    #                             <div style="background-color: #f1f1f1; text-align: center; padding: 10px;">
    #                                 <p style="font-size: 12px; color: #888888; margin: 0;">
    #                                     &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved.
    #                                 </p>
    #                             </div>
    #                         </div>
    #                     </div>
    #                 ''',
    #             }
    #             mail = self.env['mail.mail'].sudo().create(email_values)
    #             mail.send()

    #             return orangtua

    def create_orangtua(self):
        for record in self:
            """Fungsi untuk membuat akun orang tua di cdn.orangtua"""

            # if not record.password:
            #     raise UserError("Password wajib diisi terlebih dahulu sebelum membuat akun orang tua.")

            # Cek apakah email orang tua sudah ada di res.partner
            existing_partner = self.env['res.partner'].search([('email', '=', record.email_ayah)], limit=1)

            if existing_partner:
                # Jika partner sudah ada, cek apakah data orang tua sudah ada
                existing_orangtua = self.env['cdn.orangtua'].sudo().search([('partner_id', '=', existing_partner.id)], limit=1)
                if existing_orangtua:
                    # Jika data orang tua sudah ada, gunakan data tersebut
                    return existing_orangtua
                else:
                    # Jika partner ada tapi data orang tua belum ada, buat data orang tua
                    orangtua_vals = {
                        'partner_id': existing_partner.id,
                        'hubungan': 'ayah',
                        'email': record.email or record.email_ayah,
                    }
                    orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)
                    return orangtua
            else:
                partner_vals = {
                    'name': record.nama_ayah,
                    'email': record.email or record.email_ayah, 
                    'phone': record.telepon_ayah,
                    'city': record.kota_id.name,
                }
                
                # Membuat data partner untuk orang tua
                partner = self.env['res.partner'].create(partner_vals)

                orangtua_vals = {
                    'partner_id': partner.id,
                    'hubungan': 'ayah',
                    'email': record.email or record.email_ayah,
                }
                orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)

                # Mengatur password untuk user_id yang sudah dibuat otomatis
                if partner.user_id:  # Pastikan user_id sudah ada
                    password = record.password
                    partner.user_id.write({'password': password,})

                email_values = {
                    'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
                    'email_to': record.email,
                    'body_html': f'''
                        <div style="background-color: #d9eaf7; padding: 20px; font-family: Arial, sans-serif;">
                            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                                <!-- Header -->
                                <div style="background-color: #0066cc; color: #ffffff; text-align: center; padding: 20px;">
                                    <h1 style="margin: 0; font-size: 24px;">Pesantren Daarul Qur'an Istiqomah</h1>
                                </div>
                                <!-- Body -->
                                <div style="padding: 20px; color: #555555;">
                                    <p style="margin: 0 0 10px;">Assalamualaikum Wr. Wb,</p>
                                    <p style="margin: 0 0 20px;">
                                        Bapak/Ibu <strong>{record.wali_nama or record.nama_ayah or record.nama_ibu}</strong>,<br>
                                        Akun Orang Tua telah dibuat di sistem pesantren kami. Berikut adalah informasi login Anda:
                                    </p>
                                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                        <table style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px; font-weight: bold; color: #333333;">Email</td>
                                                <td style="padding: 8px; color: #555555;">{record.email}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <p style="text-align: center;">
                                        <a href="/odoo" style="background-color: #0066cc; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                                            Masuk Ke Akun Anda
                                        </a>
                                    </p>
                                    <p style="margin: 20px 0;">
                                        Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:
                                    </p>
                                    <ul style="margin: 0; padding-left: 20px; color: #555555;">
                                        <li>0822 5207 9785</li>
                                        <li>0853 9051 1124</li>
                                    </ul>
                                    <p style="margin: 20px 0;">
                                        Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.
                                    </p>
                                </div>
                                <!-- Footer -->
                                <div style="background-color: #f1f1f1; text-align: center; padding: 10px;">
                                    <p style="font-size: 12px; color: #888888; margin: 0;">
                                        &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved.
                                    </p>
                                </div>
                            </div>
                        </div>
                    ''',
                }



                # Membuat dan mengirim email
                mail = self.env['mail.mail'].sudo().create(email_values)
                mail.send()

                return orangtua


    def create_siswa(self):
        for record in self:
            """Fungsi untuk membuat data siswa dari pendaftaran"""

            jenjang_mapping = {
            'paud': 'paud',
            'tk': 'tk',
            'sdmi': 'sd',
            'smpmts': 'smp',
            'smama': 'sma',
            'smk': 'sma',  
            'nonformal': 'nonformal',
            }
        
            penghasilan_mapping = {
                '1juta' : '< Rp. 1.000.000',
                '5juta' : 'Rp. 1.000.000 - Rp. 5.000.000',
                '10juta' : 'Rp. 6.000.000 - Rp. 10.000.000',
                '11juta' : '> Rp. 10.000.000',
            }
        
            penghasilan_ibu = penghasilan_mapping.get(record.penghasilan_ibu)
            penghasilan_ayah = penghasilan_mapping.get(record.penghasilan_ayah)
            jenjang_value = jenjang_mapping.get(record.jenjang, 'paud')  
            tahun_daftar = self.tanggal_daftar.strftime('%Y')[-2:]

            siswa_vals = {
                'name'                  : record.partner_id.name,
                'propinsi_id'           : record.provinsi_id.id,
                'tanggal_daftar'        : record.tanggal_daftar,
                'nomor_pendaftaran'     : record.nomor_pendaftaran,
                'kota_id'               : record.kota_id.id,
                'kecamatan_id'          : record.kecamatan_id.id,
                'street'                : record.alamat,
                'nisn'                  : record.nisn,
                'nis'                   : record.nis,
                'nik'                   : record.nik,
                'jenjang'               : jenjang_value,
                # 'jenjang_id'            : record.jenjang_id,
                'kewarganegaraan'       : record.kewarganegaraan,
                'orangtua_id'           : record.orangtua_id.id,
                'tgl_lahir'             : record.tanggal_lahir,
                'jns_kelamin'           : record.gender,
                'tmp_lahir'             : record.kota_lahir,
                'gol_darah'             : record.golongan_darah,
                'anak_ke'               : record.anak_ke,
                'asal_sekolah'          : record.asal_sekolah,
                'status_sekolah_asal'   : record.status_sekolah_asal,
                'telp_asal_sek'         : record.telp_asal_sek,
                'alamat_asal_sek'       : record.alamat_asal_sek,
                'virtual_account'       : record.virtual_account,
                'va_saku'               : record.va_saku,

                # Orang Tua
                'ayah_nama'             : record.nama_ayah,
                'ayah_tgl_lahir'        : record.tanggal_lahir_ayah,
                'ayah_telp'             : record.telepon_ayah,
                'ayah_pekerjaan_id'     : record.pekerjaan_ayah.id,
                'ayah_email'            : record.email_ayah,
                'ayah_agama'            : record.agama_ayah,
                'ayah_warganegara'      : record.kewarganegaraan_ayah,
                'ayah_pendidikan_id'    : record.pendidikan_ayah.id,
                'ayah_penghasilan'      : penghasilan_ayah,

                'ibu_nama'              : record.nama_ibu,
                'ibu_tgl_lahir'         : record.tanggal_lahir_ibu,
                'ibu_telp'              : record.telepon_ibu,
                'ibu_pekerjaan_id'      : record.pekerjaan_ibu.id,
                'ibu_email'             : record.email_ibu,
                'ibu_agama'             : record.agama_ibu,
                'ibu_warganegara'       : record.kewarganegaraan_ibu,
                'ibu_pendidikan_id'     : record.pendidikan_ibu.id,
                'ibu_penghasilan'       : penghasilan_ibu,

                'wali_nama'             : record.wali_nama,
                'wali_tgl_lahir'        : record.wali_tgl_lahir,
                'wali_telp'             : record.wali_telp,
                'wali_email'            : record.wali_email,
                'wali_hubungan'         : record.wali_hubungan,
            }
            siswa = self.env['cdn.siswa'].sudo().create(siswa_vals)
            return siswa
    
    def generate_kode_akses(self):
        # Kombinasi karakter yang akan digunakan untuk password
        characters = string.ascii_letters + string.digits  # Huruf besar, kecil, dan angka
        # Menghasilkan password acak sepanjang 8 karakter
        kode_akses = ''.join(random.choices(characters, k=8))
        return kode_akses

    def _generate_virtual_account_temporary(self, nopen):
        for record in self:
            config_param = self.env['ir.config_parameter'].sudo()
            kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
            # account_type = "01"
            # Pastikan NIS selalu memiliki panjang tertentu
            nopen = nopen # Contoh padding NIS menjadi 6 digit

            return f"{kode_bank}{nopen}"
        
    def _generate_virtual_account_permanent(self, nis, jenjang):
        for record in self:
            config_param = self.env['ir.config_parameter'].sudo()
            kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
            account_type = "01"
            # Pastikan NIS selalu memiliki panjang tertentu
            nis = nis.replace(".", "")

            if jenjang == "sdmi":
                kode_jenjang = "10"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smpmts":
                kode_jenjang = "20"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smama":
                kode_jenjang = "30"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "nonformal":
                kode_jenjang = "40"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
        
    def _generate_va_uangsaku(self, nis, jenjang):
        for record in self:
            config_param = self.env['ir.config_parameter'].sudo()
            kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
            account_type = "02"
            # Pastikan NIS selalu memiliki panjang tertentu
            nis = nis.replace(".", "")

            if jenjang == "sdmi":
                kode_jenjang = "10"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smpmts":
                kode_jenjang = "20"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smama":
                kode_jenjang = "30"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "nonformal":
                kode_jenjang = "40"
                return f"{kode_bank}{kode_jenjang}{account_type}{nis}"

    def get_formatted_tanggal(self):
        if self.tanggal_daftar:
            return format_date(self.env, self.tanggal_daftar, date_format='dd MMMM yyyy')
        return 'Tanggal tidak tersedia'

    def get_formatted_tanggal_lahir(self):
        if self.tanggal_lahir:
            # Langsung gunakan strftime untuk format DD-MM-YYYY
            return self.tanggal_lahir.strftime('%d-%m-%Y')
        return 'Tanggal tidak tersedia'
    
    def get_formatted_tanggal_daftar(self):
        if self.tanggal_daftar:
            # Langsung gunakan strftime untuk format DD-MM-YYYY
            return self.tanggal_daftar.strftime('%d-%m-%Y')
        return 'Tanggal tidak tersedia'
    
    
    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # kuota_pendaftaran = fields.Integer(
    #     string="Kuota Pendaftaran Santri",
    #     config_parameter='pesantren_pendaftaran.kuota_pendaftaran',
    #     default=0,
    #     help="Jumlah kuota pendaftaran"
    # )
    tgl_mulai_pendaftaran = fields.Datetime(
        string="Tanggal Mulai Pendaftaran",
        config_parameter='pesantren_pendaftaran.tgl_mulai_pendaftaran',
        help="Atur tgl dibukanya pendaftaran",
    )
    tgl_akhir_pendaftaran = fields.Datetime(
        string="Tanggal Akhir Pendaftaran",
        config_parameter='pesantren_pendaftaran.tgl_akhir_pendaftaran',
        help="Atur tgl akhir dari pendaftaran",
    )
    tgl_mulai_seleksi = fields.Datetime(
        string="Tanggal Mulai Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_mulai_seleksi',
        help="Atur tgl mulai seleksi",
    )
    tgl_akhir_seleksi = fields.Datetime(
        string="Tanggal Akhir Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_akhir_seleksi',
        help="Atur tgl akhir seleksi",
    )
    tgl_pengumuman_hasil_seleksi = fields.Datetime(
        string="Tanggal Pengumuman Hasil Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
        help="Atur tgl pengumuman hasil seleksi",
    )

    is_halaman_pendaftaran = fields.Boolean(
        string="Tampilkan Halaman Pendaftaran",
        config_parameter='pesantren_pendaftaran.is_halaman_pendaftaran',
        default=True,
        help="Tampilkan halaman pendaftaran",
    )

    is_halaman_pengumuman = fields.Boolean(
        string="Tampilkan Halaman Pengumuman",
        config_parameter='pesantren_pendaftaran.is_halaman_pengumuman',
        default=False,
        help="Tampilkan halaman pengumuman",
    )

    bank        = fields.Selection(selection=[('451','BSI'),('002','BRI'),('009','BNI'),('014','BCA'),('008','MANDIRI'),('022','CIMB NIAGA'),], string='Bank Yang Digunakan', config_parameter='pesantren_pendaftaran.bank', help='Bank Yang Digunakan', default='451')
    no_rekening = fields.Char(
        string="Rekening Pembayaran", 
        config_parameter='pesantren_pendaftaran.no_rekening',
        default='7181863913',
        help="Nomor Rekening Untuk Pembayaran PSB")

    @api.model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()

        # self.env['ir.config_parameter'].set_param(
        #     'pesantren_pendaftaran.kuota_pendaftaran',
        #     self.kuota_pendaftaran
        # )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_mulai_pendaftaran',
            self.tgl_mulai_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_pendaftaran else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_akhir_pendaftaran',
            self.tgl_akhir_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_pendaftaran else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_mulai_seleksi',
            self.tgl_mulai_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_seleksi else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_akhir_seleksi',
            self.tgl_akhir_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_seleksi else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
            self.tgl_pengumuman_hasil_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_pengumuman_hasil_seleksi else False
        )

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.is_halaman_pendaftaran',
            self.is_halaman_pendaftaran
        )

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.is_halaman_pengumuman',
            self.is_halaman_pengumuman
        )

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.bank',
            self.bank
        )

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.no_rekening',
            self.no_rekening
        )

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter']
        
        # Tentukan default values jika tidak ada di ir.config_parameter
        tgl_mulai_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_mulai_pendaftaran', default=False)
        if not tgl_mulai_pendaftaran:
            tgl_mulai_pendaftaran = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_akhir_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_akhir_pendaftaran', default=False)
        if not tgl_akhir_pendaftaran:
            tgl_akhir_pendaftaran = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_mulai_seleksi = icp.get_param('pesantren_pendaftaran.tgl_mulai_seleksi', default=False)
        if not tgl_mulai_seleksi:
            tgl_mulai_seleksi = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_akhir_seleksi = icp.get_param('pesantren_pendaftaran.tgl_akhir_seleksi', default=False)
        if not tgl_akhir_seleksi:
            tgl_akhir_seleksi = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_pengumuman_hasil_seleksi = icp.get_param('pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi', default=False)
        if not tgl_pengumuman_hasil_seleksi:
            tgl_pengumuman_hasil_seleksi = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')

        res.update({
            # 'kuota_pendaftaran': int(icp.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0)),
            'tgl_mulai_pendaftaran': tgl_mulai_pendaftaran,
            'tgl_akhir_pendaftaran': tgl_akhir_pendaftaran,
            'tgl_mulai_seleksi': tgl_mulai_seleksi,
            'tgl_akhir_seleksi': tgl_akhir_seleksi,
            'tgl_pengumuman_hasil_seleksi': tgl_pengumuman_hasil_seleksi,
            'is_halaman_pendaftaran': icp.get_param('pesantren_pendaftaran.is_halaman_pendaftaran'),
            'is_halaman_pengumuman': icp.get_param('pesantren_pendaftaran.is_halaman_pengumuman'),
            'bank': icp.get_param('pesantren_pendaftaran.bank', default='451'),
            'no_rekening': icp.get_param('pesantren_pendaftaran.no_rekening', default='7181863913'),
        })
        return res


class SeleksiPenilaian(models.Model):
    _name = 'seleksi.penilaian'
    _description = 'Penilaian Seleksi Siswa Baru'

    name            = fields.Char(string='Nama Penilaian', required=True)
    soal_ids        = fields.One2many(comodel_name='seleksi.soal', inverse_name='penilaian_id', string='Soal Seleksi')
    nilai           = fields.Integer(string='Nilai Seleksi', default=0)
    penilaian_id    = fields.Many2one('seleksi.penilaian', string='Penilaian ID')  # Many2one ke penilaian lain
    daftar_soal     = fields.Text(string='Daftar Soal', compute='_compute_daftar_soal', store=True)
 
    @api.depends('soal_ids')
    def _compute_daftar_soal(self):
        for rec in self:
            rec.daftar_soal = ', '.join(soal.name for soal in rec.soal_ids)

    @api.depends('soal_ids')
    def _compute_name(self):
        for rec in self:
            rec.name = 'Penilaian: ' + ', '.join(soal.name for soal in rec.soal_ids)

    @api.onchange('soal_ids')
    def _onchange_soal_ids(self):
        # Mengisi penilaian_id berdasarkan soal_ids yang terpilih
        if self.soal_ids:
            # Ambil penilaian_id dari soal pertama yang dipilih
            self.penilaian_id = self.soal_ids[0].penilaian_id.id


class SoalSeleksi(models.Model):
    _name = 'seleksi.soal'
    _description = 'Soal untuk Seleksi Siswa Baru'

    name            = fields.Char(string='Nama Soal', required=True)
    active          = fields.Boolean(string='Aktif', default=True)
    penilaian_id    = fields.Many2one(comodel_name='seleksi.penilaian', string='Penilaian', required=True)
    nilai           = fields.Integer(string='Nilai', default=0)
    jenjang         = fields.Selection(selection=[('sdmi','SD / MI'),('smpmts','SMP / MTS'),('smama','SMA / MA'),('smk','SMK'), ('nonformal', 'Nonformal')], string='Jenjang', required=True)
    deskripsi       = fields.Text(string='Deskripsi Soal')

    @api.depends('penilaian_id', 'name')
    def _compute_name(self):
        for record in self:
            # Set the name of soal as the combination of penilaian and soal names
            record.name = '%s - %s' % (record.penilaian_id.name, record.name)

# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# from odoo.exceptions import ValidationError, UserError
# import uuid
# from datetime import datetime, timedelta
# from odoo.tools import format_date
# import pytz
# import random
# import string
# import logging

# _logger = logging.getLogger()

# class ResPartner(models.Model):
#     _inherit            = 'res.partner'

#     virtual_account     = fields.Char(string='Virtual Account', store=True)
#     va_saku             = fields.Char(string='No. VA Uang Saku', store=True)
#     bank                = fields.Many2one('ubig.bank', string="Bank", help="Pilih bank untuk membuat virtual account")
#     petunjuk_pembayaran = fields.Text(related='bank.petunjuk_pembayaran', string="Petunjuk Pembayaran")
#     jns_partner         = fields.Selection(string='Jenis Partner', selection=[
#                         ('siswa', 'Siswa'), 
#                         ('ortu', 'Orang Tua'), 
#                         ('guru', 'Guru'), 
#                         ('umum', 'Umum'), 
#                         ('calon_santri', 'Calon Santri')]
#                         , default="calon_santri", readonly="true")

# class DataPendaftaran(models.Model):
#     _name               = 'ubig.pendaftaran'
#     _inherit            = ['mail.thread', 'mail.activity.mixin']
#     _inherits           = {"res.partner": "partner_id"}
#     _description        = 'Data Pendaftaran'
#     _order              = 'total_nilai desc'
    

#     token               = fields.Char(string='Token')
#     nomor_pendaftaran   = fields.Char(string='No Pendaftaran', readonly=True)
#     tanggal_daftar      = fields.Date(string='Tanggal Daftar', default=fields.Date.context_today)
#     partner_id          = fields.Many2one('res.partner', string="Nama Santri", required=False, help="Nama Calon Santri")

#     # Username
#     nik                 = fields.Char(string="NIK", help="Nomor Induk Keluarga Calon santri")
#     email               = fields.Char(string="email", help="Email Calon Santri")
#     password            = fields.Char(string="Kata Sandi", help="Kata Sandi Login")
#     nomor_hp            = fields.Char(string="Nomor HP", help="Nomor HP/WhatsApp Calon Santri")
#     nomor_login         = fields.Char(string="Nomor HP", help="Nomor HP/WhatsApp Untuk Login")

#     # Jenjang Calon Santri
#     jenjang_id          = fields.Many2one('ubig.pendidikan', string="Jenjang Pendidikan")
#     jenjang             = fields.Selection(related='jenjang_id.jenjang', string='Jenjang', readonly=True)
#     biaya               = fields.Integer(related='jenjang_id.biaya', string='Biaya Pendaftaran', readonly=True)
#     keterangan          = fields.Char(related='jenjang_id.keterangan', string='Keterangan', readonly=True)

#     # Data Diri
#     gender              = fields.Selection([('L','Laki - Laki'),('P','Perempuan'),], string="Jenis Kelamin")
#     kota_lahir          = fields.Char(string="Kota Kelahiran")
#     tanggal_lahir       = fields.Date(string="Tanggal Lahir Calon Santri")
#     golongan_darah      = fields.Selection([
#                         ('A', 'A'),
#                         ('B', 'B'),
#                         ('AB', 'AB'),
#                         ('O', 'O'),
#                         ], string="Golongan Darah")
#     kewarganegaraan     = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Kewarganegaraan",  help="")
#     alamat              = fields.Char(string='Alamat Calon Santri')
#     provinsi_id         = fields.Many2one(comodel_name="cdn.ref_propinsi",  string="Provinsi",  help="")
#     kota_id             = fields.Many2one(comodel_name="cdn.ref_kota",  string="Kota",  help="")
#     kecamatan_id        = fields.Many2one(comodel_name="cdn.ref_kecamatan",  string="Kecamatan",  help="")
#     nisn                = fields.Char(string="NISN")
#     nis                 = fields.Char(string="NIS", store=True,  required=False, copy=False, readonly=True, default=lambda self: self._generate_nis())
#     anak_ke             = fields.Integer( string="Anak ke",  help="")
#     jml_saudara_kandung = fields.Integer( string="Jml Saudara Kandung",  help="")
#     cita_cita           = fields.Char(string='Cita-Cita')

#     # Data Pendidikan
#     asal_sekolah        = fields.Char(string='Asal Sekolah')
#     alamat_asal_sek     = fields.Char(string='Alamat Sekolah Asal')
#     telp_asal_sek       = fields.Char(string='No Telp Sekolah Asal')
#     status_sekolah_asal = fields.Selection(string='Status Sekolah Asal', selection=[('swasta', 'Swasta'), ('negeri', 'Negeri'),])
#     npsn                = fields.Char(string='NPSN Sekolah')

#     # Data Orang Tua - Ayah
#     nama_ayah           = fields.Char(string="Nama Ayah")
#     ktp_ayah            = fields.Char(string="Nomor KTP Ayah")
#     tanggal_lahir_ayah  = fields.Date(string="Tanggal Lahir Ayah")
#     telepon_ayah        = fields.Char(string="Nomor Telepon Ayah")
#     pekerjaan_ayah      = fields.Many2one('cdn.ref_pekerjaan',string="Pekerjaan Ayah")
#     penghasilan_ayah    = fields.Selection([
#                         ('1juta', ' < Rp. 1.000.000'),
#                         ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
#                         ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
#                         ('11juta', '> Rp. 10.000.000')
#                         ], string="Penghasilan Ayah")
#     email_ayah          = fields.Char(string="Email Ayah")
#     agama_ayah          = fields.Selection([
#                         ('islam', 'Islam'),
#                         ('kristen', 'Kristen'),
#                         ('katolik', 'Katolik'),
#                         ('hindu', 'Hindu'),
#                         ('budha', 'Budha'),
#                         ('lainnya', 'Lainnya'),
#                         ], string="Agama Ayah")
#     kewarganegaraan_ayah = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan Ayah")
#     pendidikan_ayah     = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan Ayah")

#     # Data Orang Tua - Ibu
#     nama_ibu            = fields.Char(string="Nama Ibu")
#     ktp_ibu             = fields.Char(string="Nomor KTP Ibu")
#     tanggal_lahir_ibu   = fields.Date(string="Tanggal Lahir Ibu")
#     telepon_ibu         = fields.Char(string="Nomor Telepon Ibu")
#     pekerjaan_ibu       = fields.Many2one('cdn.ref_pekerjaan', string="Pekerjaan Ibu")
#     penghasilan_ibu     = fields.Selection([
#                         ('1juta', ' < Rp. 1.000.000'),
#                         ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
#                         ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
#                         ('11juta', '> Rp. 10.000.000')
#                         ], string="Penghasilan Ibu")
#     email_ibu           = fields.Char(string="Email Ibu")
#     agama_ibu           = fields.Selection([
#                         ('islam', 'Islam'),
#                         ('kristen', 'Kristen'),
#                         ('katolik', 'Katolik'),
#                         ('hindu', 'Hindu'),
#                         ('budha', 'Budha'),
#                         ('lainnya', 'Lainnya'),
#                         ], string="Agama Ibu")
#     kewarganegaraan_ibu = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan Ibu")
#     pendidikan_ibu      = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan Ibu")

#     wali_nama           = fields.Char( string="Nama Wali",  help="")
#     wali_tmp_lahir      = fields.Char( string="Tmp lahir (Wali)",  help="")
#     wali_tgl_lahir      = fields.Date( string="Tgl lahir (Wali)",  help="")
#     wali_telp           = fields.Char( string="No Telepon (Wali)",  help="")
#     wali_email          = fields.Char( string="Email (Wali)",  help="")
#     wali_password       = fields.Char( string="Password", help="")
#     wali_agama          = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Wali)",  help="")
#     wali_hubungan       = fields.Char( string="Hubungan dengan Siswa",  help="")

#     # Dokumen Anak
#     akta_kelahiran      = fields.Binary(string="Akta Kelahiran")
#     kartu_keluarga      = fields.Binary(string="Kartu Keluarga")
#     ijazah              = fields.Binary(string="Ijazah")
#     surat_kesehatan     = fields.Binary(string="Surat Keterangan Sehat")
#     pas_foto            = fields.Binary(string="Pas Foto Berwarna")
#     skhun               = fields.Binary(string="SKHUN")
#     raport_terakhir     = fields.Binary(string="Raport Terakhir")

#     # Dokumen Orang Tua
#     ktp_ortu            = fields.Binary(string="KTP Orang Tua/Wali")

#     # Aspek Penilaian
#     soal_ids            = fields.Many2many('seleksi.penilaian', string="Detail Penilaian")

#     # Computed field untuk total nilai
#     total_nilai         = fields.Integer(string="Total Nilai", compute="_compute_total_nilai", store=True)

#     orangtua_id         = fields.Many2one('cdn.orangtua', string="Data Orang Tua", readonly=True)
#     siswa_id            = fields.Many2one('cdn.siswa', string="Data Siswa", readonly=True)

#     status_va           = fields.Selection([
#                             ('temporary', 'Temporary'),
#                             ('permanent', 'Permanent'),
#                             ('inactive', 'Inactive'),
#                         ], string="Status Virtual Account", default='temporary')

#     # kode_akses          = fields.Char(string="Kode Akses")

#     bukti_pembayaran = fields.Binary(string="Bukti Pembayaran")
#     status_pembayaran = fields.Selection([
#         ('belumbayar','Belum Bayar'),
#         ('sudahbayar','Sudah Bayar')
#         ], string="Status Pembayaran", default="belumbayar")

#     # perubahan
#     is_alumni = fields.Boolean(string='Alumni DQI', default=False)
#     is_pindahan_sd = fields.Boolean(string='Pindahan SD', default=False)

#     # State
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('terdaftar', 'Terdaftar'),
#         ('seleksi', 'Seleksi'),
#         ('diterima', 'Diterima'),
#         ('ditolak', 'Ditolak'),
#         ('batal', 'Batal'),
#     ], string='Status', default='draft',
#         track_visibility='onchange')

#     @api.depends('soal_ids')

#     def _compute_total_nilai(self):
#         for record in self:
#             # Menghitung total nilai dari soal_ids
#             record.total_nilai = sum(soal.nilai for soal in record.soal_ids if soal.nilai)

#     @api.model
#     def create(self, vals):
#         # Get the current year
#         current_year = fields.Date.context_today(self).year % 100
        
#         # Search for existing records with the same year
#         existing_records = self.search([('nomor_pendaftaran', 'ilike', f'{current_year}%')])
        
#         # Determine the next sequence number
#         if existing_records:
#             last_number = max(int(record.nomor_pendaftaran[len(str(current_year)):]) for record in existing_records)
#             next_number = last_number + 1
#         else:
#             next_number = 1
            
#         # Generate the new nomor_pendaftaran
#         vals['nomor_pendaftaran'] = f'{current_year}{str(next_number).zfill(4)}'

#         # Generate UUID token
#         vals['token'] = str(uuid.uuid4())

#         record = super(DataPendaftaran, self).create(vals)

#         if record.state == 'draft':
#             # Buat data virtual account
#             if not record.virtual_account:
#                 nopen = record.nomor_pendaftaran
#                 record.virtual_account = record._generate_virtual_account_temporary(nopen)
#                 record.status_va = 'temporary'
#         return record

#     # def get_psb_statistics(self):
#     #     total_pendaftar = self.search_count([])
#     #     total_diterima = self.search_count([('state', '=', 'diterima')])
        
#     #     # Mengambil nilai kuota pendaftaran dari ir.config_parameter
#     #     config_param = self.env['ir.config_parameter'].sudo()
#     #     kuota_pendaftaran = int(config_param.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0))

#     #     sisa_kuota = kuota_pendaftaran - total_pendaftar

#     #     return {
#     #         'total_pendaftar': total_pendaftar,
#     #         'total_diterima': total_diterima,
#     #         'kuota_pendaftaran': kuota_pendaftaran,
#     #         'sisa_kuota': max(sisa_kuota, 0),  # Pastikan tidak negatif
#     #     }
    
#     def hapus_pendaftaran_kadaluarsa(self):
#         # Tentukan zona waktu Anda, misalnya 'Asia/Jakarta' untuk WIB
#         timezone = pytz.timezone('Asia/Jakarta')
#         for record in self:
#             if record.tanggal_daftar:
#                 tgl_hari_ini = datetime.now(timezone).date()
#                 batas_waktu = record.tanggal_daftar + timedelta(days=7)

#                 # Debug
#                 # raise UserError(f"Tanggal setelah satu hari: {batas_waktu}, Tanggal hari ini: {tgl_hari_ini}")

#                 if tgl_hari_ini > batas_waktu:
#                     pendaftaran_kadaluarsa = self.search([('state', '=', 'draft')])
#                     pendaftaran_kadaluarsa.unlink()

#     def action_terdaftar(self):
#         self.state = 'terdaftar'

#     def action_seleksi(self):
#         self.state = 'seleksi'

#     def action_diterima(self):
#         self.state = 'diterima'

#     def action_ditolak(self):
#         self.state = 'ditolak'

#     def action_batal(self):
#         self.state = 'batal'

#     def action_draft(self):
#         # Optional: You can define additional actions for when "Draft" is clicked
#         self.write({'state': 'draft'})


#     def action_report_pendaftaran(self):
#         # Logika untuk meng-generate laporan PDF atau aksi lainnya
#         return self.env.ref('pesantren_pendaftaran.action_report_pendaftaran').report_action(self)

#     # @api.model
#     # def default_get(self, fields):
#     # res = super(DataPendaftaran, self).default_get(fields)  # Use the exact class name here
#     # res['jns_partner'] = 'calon_santri'
#     # return res

#     def write(self, vals):

#         if 'status_pembayaran' in vals and vals['status_pembayaran'] == 'sudahbayar':
#             self._create_journal_entry()

#         if 'state' in vals and vals['state'] == 'diterima':
#             for record in self:
#                 # Buat akun orang tua jika belum ada
#                 if not record.orangtua_id:
#                     orangtua = record.create_orangtua()
#                     record.orangtua_id = orangtua.id

#                 # Buat data siswa jika belum ada
#                 if not record.siswa_id:
#                     siswa = record.create_siswa()
#                     record.siswa_id = siswa.id

#                 # Buat data virtual account
#                 # if not record.virtual_account:
#                 #     nisn = record.nisn
#                 #     record.virtual_account = record._generate_virtual_account(nisn)
#                 nis = record.nis
#                 jenjang = record.jenjang
#                 record.virtual_account = record._generate_virtual_account_permanent(nis, jenjang)
#                 record.status_va = 'permanent'

#                 # Buat data virtual account uang saku
#                 if not record.va_saku:
#                     record.va_saku = record._generate_va_uangsaku(nis, jenjang)

#                 # Generate nis
#                 # if not record.nis:
#                 #     nisn = record.nisn
#                 #     record.nis = record._generate_nis(nisn)

#         if 'state' in vals and vals['state'] == 'ditolak':
#             for record in self:
#                 record.virtual_account = False # Menghapus Virtual Account
#                 record.status_va = 'inactive'

#         # Check if state is being changed to 'terdaftar'
#         # if 'state' in vals and vals['state'] == 'diterima':
#         #     for record in self:
#         #         if not record.virtual_account:
#         #             record.virtual_account = "01" + record._generate_virtual_account()

#         return super(DataPendaftaran, self).write(vals)
    
#     def _create_journal_entry(self):
#         """Mencatat jurnal secara otomatis."""
#         for rec in self:
#             if rec.status_pembayaran != 'sudahbayar':
#                 continue  # Lewati jika status bukan "sudah_bayar"

#             # Ambil jurnal tipe "Cash"
#             journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
#             if not journal:
#                 raise ValidationError('Tidak ada jurnal tipe "Cash" yang ditemukan.')

#             if not journal.default_account_id:
#                 raise ValidationError("Akun default tidak diatur untuk jurnal ini.")
            
#             # Dapatkan akun debit dan kredit
#             debit_account = journal.default_account_id
#             credit_account = self.env['account.account'].search([('code', '=', '11110001')], limit=1)  # Sesuaikan dengan akun Anda

#             if not credit_account:
#                 raise ValidationError("Akun kredit tidak ditemukan.")

#             if not credit_account:
#                 raise ValidationError("Akun kredit tidak ditemukan.")

#             # Buat journal entry
#             move = self.env['account.move'].create({
#                 'journal_id': journal.id,
#                 'date': fields.Date.today(),
#                 'line_ids': [
#                     (0, 0, {
#                         'account_id': debit_account.id,
#                         'partner_id': self.partner_id.id if self.partner_id else False,
#                         'name': 'Debit Entry',
#                         'debit': self.biaya,
#                         'credit': 0.0,
#                     }),
#                     (0, 0, {
#                         'account_id': credit_account.id,
#                         'partner_id': self.partner_id.id if self.partner_id else False,
#                         'name': 'Credit Entry',
#                         'debit': 0.0,
#                         'credit': self.biaya,
#                     }),
#                 ],
#             })
#             move.action_post()
    
#     def create_orangtua(self):
#         for record in self:
#             """Fungsi untuk membuat akun orang tua di cdn.orangtua"""

#             # Cek apakah email orang tua sudah ada di res.partner
#             existing_partner = self.env['res.partner'].search([('email', '=', record.wali_email)], limit=1)

#             if existing_partner:
#                 # Jika partner sudah ada, cek apakah data orang tua sudah ada
#                 existing_orangtua = self.env['cdn.orangtua'].sudo().search([('partner_id', '=', existing_partner.id)], limit=1)
#                 if existing_orangtua:
#                     # Jika data orang tua sudah ada, gunakan data tersebut
#                     return existing_orangtua
#                 else:
#                     # Jika partner ada tapi data orang tua belum ada, buat data orang tua
#                     orangtua_vals = {
#                         'partner_id': existing_partner.id,
#                         'hubungan': 'wali',
#                         'email': record.email,
#                     }
#                     orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)
#                     return orangtua
#             else:
#                 # Jika partner belum ada, buat data partner baru
#                 # Membuat data orangtua otomatis saat pendaftaran diterima
#                 partner_vals = {
#                     'name': record.wali_nama,
#                     'email': record.email or record.nomor_login,  # Asumsi field email ada di model Pendaftaran
#                     'phone': record.wali_telp,  # Asumsi field phone ada di model Pendaftaran
#                     'city': record.kota_id.name,
#                 }
                
#                 # Membuat data partner untuk orang tua
#                 partner = self.env['res.partner'].create(partner_vals)

#                 orangtua_vals = {
#                     'partner_id': partner.id,
#                     'hubungan': 'wali',
#                     'email': record.email,
#                 }
#                 orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)

#                 # Mengatur password untuk user_id yang sudah dibuat otomatis
#                 if partner.user_id:  # Pastikan user_id sudah ada
#                     password = record.password
#                     partner.user_id.write({'password': password,})

#                 email_values = {
#                     'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
#                     'email_to': record.email,
#                     'body_html': f'''
#                         <div style="background-color: #d9eaf7; padding: 20px; font-family: Arial, sans-serif;">
#                             <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
#                                 <!-- Header -->
#                                 <div style="background-color: #0066cc; color: #ffffff; text-align: center; padding: 20px;">
#                                     <h1 style="margin: 0; font-size: 24px;">Pesantren Daarul Qur'an Istiqomah</h1>
#                                 </div>
#                                 <!-- Body -->
#                                 <div style="padding: 20px; color: #555555;">
#                                     <p style="margin: 0 0 10px;">Assalamualaikum Wr. Wb,</p>
#                                     <p style="margin: 0 0 20px;">
#                                         Bapak/Ibu <strong>{record.wali_nama or record.nama_ayah or record.nama_ibu}</strong>,<br>
#                                         Akun Orang Tua telah dibuat di sistem pesantren kami. Berikut adalah informasi login Anda:
#                                     </p>
#                                     <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
#                                         <table style="width: 100%; border-collapse: collapse;">
#                                             <tr>
#                                                 <td style="padding: 8px; font-weight: bold; color: #333333;">Email</td>
#                                                 <td style="padding: 8px; color: #555555;">{record.email}</td>
#                                             </tr>
#                                         </table>
#                                     </div>
#                                     <p style="text-align: center;">
#                                         <a href="/odoo" style="background-color: #0066cc; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
#                                             Masuk Ke Akun Anda
#                                         </a>
#                                     </p>
#                                     <p style="margin: 20px 0;">
#                                         Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:
#                                     </p>
#                                     <ul style="margin: 0; padding-left: 20px; color: #555555;">
#                                         <li>0822 5207 9785</li>
#                                         <li>0853 9051 1124</li>
#                                     </ul>
#                                     <p style="margin: 20px 0;">
#                                         Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.
#                                     </p>
#                                 </div>
#                                 <!-- Footer -->
#                                 <div style="background-color: #f1f1f1; text-align: center; padding: 10px;">
#                                     <p style="font-size: 12px; color: #888888; margin: 0;">
#                                         &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved.
#                                     </p>
#                                 </div>
#                             </div>
#                         </div>
#                     ''',
#                 }



#                 # Membuat dan mengirim email
#                 mail = self.env['mail.mail'].sudo().create(email_values)
#                 mail.send()

#                 return orangtua

#     def create_siswa(self):
#         for record in self:
#             """Fungsi untuk membuat data siswa dari pendaftaran"""
#             siswa_vals = {
#                 'name'                  : record.partner_id.name,
#                 'propinsi_id'           : record.provinsi_id.id,
#                 'kota_id'               : record.kota_id.id,
#                 'kecamatan_id'          : record.kecamatan_id.id,
#                 'street'                : record.alamat,
#                 'nisn'                  : record.nisn,
#                 'nis'                   : record.nis,
#                 'nik'                   : record.nik,
#                 'jenjang'               : record.jenjang,
#                 'kewarganegaraan'       : record.kewarganegaraan,
#                 'orangtua_id'           : record.orangtua_id.id,
#                 'tgl_lahir'             : record.tanggal_lahir,
#                 'jns_kelamin'           : record.gender,
#                 'tmp_lahir'             : record.kota_lahir,
#                 'gol_darah'             : record.golongan_darah,
#                 'anak_ke'               : record.anak_ke,
#                 'asal_sekolah'          : record.asal_sekolah,
#                 'status_sekolah_asal'   : record.status_sekolah_asal,
#                 'telp_asal_sek'         : record.telp_asal_sek,
#                 'alamat_asal_sek'       : record.alamat_asal_sek,
#                 'virtual_account'       : record.virtual_account,
#                 'va_saku'               : record.va_saku,

#                 # Orang Tua
#                 'ayah_nama'             : record.nama_ayah,
#                 'ayah_tgl_lahir'        : record.tanggal_lahir_ayah,
#                 'ayah_telp'             : record.telepon_ayah,
#                 'ayah_pekerjaan_id'     : record.pekerjaan_ayah.id,
#                 'ayah_agama'            : record.agama_ayah,
#                 'ayah_warganegara'      : record.kewarganegaraan_ayah,
#                 'ayah_pendidikan_id'    : record.pendidikan_ayah.id,

#                 'ibu_nama'              : record.nama_ibu,
#                 'ibu_tgl_lahir'         : record.tanggal_lahir_ibu,
#                 'ibu_telp'              : record.telepon_ibu,
#                 'ibu_pekerjaan_id'      : record.pekerjaan_ibu.id,
#                 'ibu_agama'             : record.agama_ibu,
#                 'ibu_warganegara'       : record.kewarganegaraan_ibu,
#                 'ibu_pendidikan_id'     : record.pendidikan_ibu.id,

#                 'wali_nama'             : record.wali_nama,
#                 'wali_tgl_lahir'        : record.wali_tgl_lahir,
#                 'wali_telp'             : record.wali_telp,
#                 'wali_email'            : record.wali_email,
#                 'wali_hubungan'         : record.wali_hubungan,
#             }
#             siswa = self.env['cdn.siswa'].sudo().create(siswa_vals)
#             return siswa
    
#     def generate_kode_akses(self):
#         # Kombinasi karakter yang akan digunakan untuk password
#         characters = string.ascii_letters + string.digits  # Huruf besar, kecil, dan angka
#         # Menghasilkan password acak sepanjang 8 karakter
#         kode_akses = ''.join(random.choices(characters, k=8))
#         return kode_akses

#     def _generate_virtual_account_temporary(self, nopen):
#         for record in self:
#             config_param = self.env['ir.config_parameter'].sudo()
#             kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
#             # account_type = "01"
#             # Pastikan NIS selalu memiliki panjang tertentu
#             nopen = nopen # Contoh padding NIS menjadi 6 digit

#             return f"{kode_bank}{nopen}"
        
#     def _generate_virtual_account_permanent(self, nis, jenjang):
#         for record in self:
#             config_param = self.env['ir.config_parameter'].sudo()
#             kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
#             account_type = "01"
#             # Pastikan NIS selalu memiliki panjang tertentu
#             nis = nis

#             if jenjang == "sdmi":
#                 kode_jenjang = "10"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
#             elif jenjang == "smpmts":
#                 kode_jenjang = "20"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
#             elif jenjang == "smama":
#                 kode_jenjang = "30"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
        
#     def _generate_va_uangsaku(self, nis, jenjang):
#         for record in self:
#             config_param = self.env['ir.config_parameter'].sudo()
#             kode_bank = config_param.get_param('pesantren_pendaftaran.bank', default='451')
#             account_type = "02"
#             # Pastikan NIS selalu memiliki panjang tertentu
#             nis = nis

#             if jenjang == "sdmi":
#                 kode_jenjang = "10"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
#             elif jenjang == "smpmts":
#                 kode_jenjang = "20"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"
#             elif jenjang == "smama":
#                 kode_jenjang = "30"
#                 return f"{kode_bank}{kode_jenjang}{account_type}{nis}"

#     def get_formatted_tanggal(self):
#         if self.tanggal_daftar:
#             return format_date(self.env, self.tanggal_daftar, date_format='dd MMMM yyyy')
#         return 'Tanggal tidak tersedia'

#     def get_formatted_tanggal_lahir(self):
#         if self.tanggal_lahir:
#             # Langsung gunakan strftime untuk format DD-MM-YYYY
#             return self.tanggal_lahir.strftime('%d-%m-%Y')
#         return 'Tanggal tidak tersedia'
    
#     def get_formatted_tanggal_daftar(self):
#         if self.tanggal_daftar:
#             # Langsung gunakan strftime untuk format DD-MM-YYYY
#             return self.tanggal_daftar.strftime('%d-%m-%Y')
#         return 'Tanggal tidak tersedia'
    
    
#     # @api.model
#     # def create(self, vals):
#     #     """Otomatis membuat Token & NIP saat karyawan baru didaftarkan"""
#     #     # vals['token'] = str(uuid.uuid4())  # Generate Token

#     #     record = super(DataPendaftaran, self).create(vals)

#     #     # Setelah record dibuat, ambil data dari instance model
#     #     # nis = self._generate_nis(record)
#     #     # if nis:
#     #     #     record.nis = nis  # Simpan NIP ke record

#     #     return record
    
    
#     @api.model
#     def _generate_nomor_pendaftaran(self):
#         last_record = self.search([], order="nomor_pendaftaran desc", limit=1)
#         if last_record and last_record.nomor_pendaftaran:
#             last_number = int(last_record.nomor_pendaftaran[-3:]) + 1
#         else:
#             last_number = 1
#         return f"001{str(last_number).zfill(3)}"
    
#     def _generate_nis(self, record=None):
#         """Fungsi untuk membuat NIS otomatis"""
#         if record is None:
#             record = self

#         if not record.nomor_pendaftaran and record.tanggal_daftar:
#             _logger.warning("NIS tidak bisa dibuat: Tanggal lahir atau lembaga kosong.")
#             return False

#         # Mapping Kode Lembaga
#         lembaga = {
#             'paud': '01', 'tk': '02', 'sdmi': '03',
#             'smpmts': '04', 'smama': '05', 'smk': '06'
#         }.get(record.jenjang, '00')

#         # Konversi Tahun Lahir
#         if record.tanggal_daftar:
#             try:
#                 tanggal = record.tanggal_daftar.strftime('%Y')[-2:]
#             except AttributeError:
#                 tanggal = '00'
#         else:
#             tanggal= '00'

#         # # Generate 4 Digit Random
#         # random_digits = ''.join(random.choices(string.digits, k=4))
#         nomor = record.nomor_pendaftaran 
#         # Format NIP
#         nis = f"{lembaga}.{tanggal}.{nomor}"
#         # _logger.info(f"NIP yang dihasilkan: {nip}")  # Log hasil NIP
#         return nis
    
#     @api.constrains('nis')
#     def _check_nis(self):
#         """Validasi NIS tidak boleh kosong dan minimal 8 karakter"""
#         for record in self:
#             if record.nis and len(record.nis) < 2:
#                 raise ValidationError("NIS harus memiliki minimal 8 karakter. Silakan periksa kembali.")

#     @api.model
#     def create(self, vals):
#         _logger.info(f"Vals sebelum create: {vals}")
#         record = super(DataPendaftaran, self).create(vals)
        
#         if record is None:
#             record = self

#         if record.state == 'diterima':  # Generate NIS hanya jika santri diterima
#             nis = self._generate_nis(record)
#             if nis:
#                 record.nis = nis  # Simpan NIS ke record

#         _logger.info(f"NIS setelah create: {record.nis}")
#         return record
    
    
    
    
#     # @api.model
#     # def create(self, vals):
#     #     # Pastikan NIS dibuat saat pendaftaran diterima
#     #     record = super(DataPendaftaran, self).create(vals)
#     #     if record.state == 'diterima':
#     #         record._create_santri()
#     #     return record

#     # def write(self, vals):
#     #     res = super(DataPendaftaran, self).write(vals)
#     #     if 'state' in vals and vals['state'] == 'diterima':
#     #         self._create_santri()
#     #     return res

#     # def _create_santri(self):
#     #     """ Membuat santri baru dan mengenerate NIS otomatis """
#     #     for record in self:
#     #         if not record.partner_id:
#     #             # Buat santri baru
#     #             santri_vals = {
#     #                 'name': record.name,
#     #                 'pendaftaran_id': record.id,
#     #             }
#     #             santri = self.env['cdn.santri'].create(santri_vals)
#     #             record.partner_id = santri.id 
#     #             santri.generate_nis()
    
    
    
#     # @api.model
#     # def create(self, vals):
#     #     record = super(DataPendaftaran, self).create(vals)
#     #     record.nis = record._generate_nis()  # Hapus "record=" dari pemanggilan
#     #     return record

    
#     # @api.depends('state')
#     # def _generate_nis(self, record=None):
#     #     """Fungsi untuk membuat NIS otomatis"""
#     #     for record in self:
#     #         # Mapping Kode Lembaga
#     #         kode_lembaga = {
#     #             'paud': '01', 'tk': '02', 'sdmi': '03',
#     #             'smpmts': '04', 'smama': '05', 'smk': '06'
#     #         }.get(record.jenjang, '00')

#     #         # Konversi Tahun Masuk
#     #         if record.tanggal_daftar:
#     #             try:
#     #                 tahun_masuk = record.tanggal_daftar.strftime('%Y')[-2:]
#     #             except AttributeError:
#     #                 tahun_masuk = '00'
#     #         else:
#     #             tahun_masuk = '00'

#     #         # Nomor pendaftaran
#     #         nomor = record.nomor_pendaftaran if record.nomor_pendaftaran else '00000'

#     #         # Format NIS
#     #         nis = f"{kode_lembaga}.{tahun_masuk}.{nomor}"

#     #         return nis

                
#     # def write(self, vals):
#     #     res = super(DataPendaftaran, self).write(vals)
#     #     for record in self:
#     #         record.nis = record._generate_nis()  # Hapus "record=" dari pemanggilan
#     #     return res
    
#     # @api.constrains('nis')
#     # def _check_nis(self):
#     #     """Validasi NIS tidak boleh kosong dan minimal 8 karakter"""
#     #     for record in self:
#     #         if record.nis and len(record.nis) < 8:
#     #             raise ValidationError("NIS harus memiliki minimal 8 karakter. Silakan periksa kembali.")

#     # @api.model
#     # def create(self, vals):
#     #     record = super(DataPendaftaran, self).create(vals)

#     #     nis = self._generate_nis(record=record)
#     #     if nis:
#     #         record.nis = nis  # Simpan NIS ke record

#     #     return record
    
    

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     # kuota_pendaftaran = fields.Integer(
#     #     string="Kuota Pendaftaran Santri",
#     #     config_parameter='pesantren_pendaftaran.kuota_pendaftaran',
#     #     default=0,
#     #     help="Jumlah kuota pendaftaran"
#     # )
#     tgl_mulai_pendaftaran = fields.Datetime(
#         string="Tanggal Mulai Pendaftaran",
#         config_parameter='pesantren_pendaftaran.tgl_mulai_pendaftaran',
#         help="Atur tgl dibukanya pendaftaran",
#     )
#     tgl_akhir_pendaftaran = fields.Datetime(
#         string="Tanggal Akhir Pendaftaran",
#         config_parameter='pesantren_pendaftaran.tgl_akhir_pendaftaran',
#         help="Atur tgl akhir dari pendaftaran",
#     )
#     tgl_mulai_seleksi = fields.Datetime(
#         string="Tanggal Mulai Seleksi",
#         config_parameter='pesantren_pendaftaran.tgl_mulai_seleksi',
#         help="Atur tgl mulai seleksi",
#     )
#     tgl_akhir_seleksi = fields.Datetime(
#         string="Tanggal Akhir Seleksi",
#         config_parameter='pesantren_pendaftaran.tgl_akhir_seleksi',
#         help="Atur tgl akhir seleksi",
#     )
#     tgl_pengumuman_hasil_seleksi = fields.Datetime(
#         string="Tanggal Pengumuman Hasil Seleksi",
#         config_parameter='pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
#         help="Atur tgl pengumuman hasil seleksi",
#     )

#     is_halaman_pendaftaran = fields.Boolean(
#         string="Tampilkan Halaman Pendaftaran",
#         config_parameter='pesantren_pendaftaran.is_halaman_pendaftaran',
#         default=True,
#         help="Tampilkan halaman pendaftaran",
#     )

#     is_halaman_pengumuman = fields.Boolean(
#         string="Tampilkan Halaman Pengumuman",
#         config_parameter='pesantren_pendaftaran.is_halaman_pengumuman',
#         default=False,
#         help="Tampilkan halaman pengumuman",
#     )

#     bank        = fields.Selection(selection=[('451','BSI'),('002','BRI'),('009','BNI'),('014','BCA'),('008','MANDIRI'),('022','CIMB NIAGA'),], string='Bank Yang Digunakan', config_parameter='pesantren_pendaftaran.bank', help='Bank Yang Digunakan', default='451')
#     no_rekening = fields.Char(
#         string="Rekening Pembayaran", 
#         config_parameter='pesantren_pendaftaran.no_rekening',
#         default='7181863913',
#         help="Nomor Rekening Untuk Pembayaran PSB")

#     @api.model
#     def set_values(self):
#         res = super(ResConfigSettings, self).set_values()

#         # self.env['ir.config_parameter'].set_param(
#         #     'pesantren_pendaftaran.kuota_pendaftaran',
#         #     self.kuota_pendaftaran
#         # )
#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.tgl_mulai_pendaftaran',
#             self.tgl_mulai_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_pendaftaran else False
#         )
#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.tgl_akhir_pendaftaran',
#             self.tgl_akhir_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_pendaftaran else False
#         )
#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.tgl_mulai_seleksi',
#             self.tgl_mulai_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_seleksi else False
#         )
#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.tgl_akhir_seleksi',
#             self.tgl_akhir_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_seleksi else False
#         )
#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
#             self.tgl_pengumuman_hasil_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_pengumuman_hasil_seleksi else False
#         )

#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.is_halaman_pendaftaran',
#             self.is_halaman_pendaftaran
#         )

#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.is_halaman_pengumuman',
#             self.is_halaman_pengumuman
#         )

#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.bank',
#             self.bank
#         )

#         self.env['ir.config_parameter'].set_param(
#             'pesantren_pendaftaran.no_rekening',
#             self.no_rekening
#         )

#         return res

#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         icp = self.env['ir.config_parameter']
        
#         # Tentukan default values jika tidak ada di ir.config_parameter
#         tgl_mulai_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_mulai_pendaftaran', default=False)
#         if not tgl_mulai_pendaftaran:
#             tgl_mulai_pendaftaran = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

#         tgl_akhir_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_akhir_pendaftaran', default=False)
#         if not tgl_akhir_pendaftaran:
#             tgl_akhir_pendaftaran = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')

#         tgl_mulai_seleksi = icp.get_param('pesantren_pendaftaran.tgl_mulai_seleksi', default=False)
#         if not tgl_mulai_seleksi:
#             tgl_mulai_seleksi = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')

#         tgl_akhir_seleksi = icp.get_param('pesantren_pendaftaran.tgl_akhir_seleksi', default=False)
#         if not tgl_akhir_seleksi:
#             tgl_akhir_seleksi = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')

#         tgl_pengumuman_hasil_seleksi = icp.get_param('pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi', default=False)
#         if not tgl_pengumuman_hasil_seleksi:
#             tgl_pengumuman_hasil_seleksi = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')

#         res.update({
#             # 'kuota_pendaftaran': int(icp.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0)),
#             'tgl_mulai_pendaftaran': tgl_mulai_pendaftaran,
#             'tgl_akhir_pendaftaran': tgl_akhir_pendaftaran,
#             'tgl_mulai_seleksi': tgl_mulai_seleksi,
#             'tgl_akhir_seleksi': tgl_akhir_seleksi,
#             'tgl_pengumuman_hasil_seleksi': tgl_pengumuman_hasil_seleksi,
#             'is_halaman_pendaftaran': icp.get_param('pesantren_pendaftaran.is_halaman_pendaftaran'),
#             'is_halaman_pengumuman': icp.get_param('pesantren_pendaftaran.is_halaman_pengumuman'),
#             'bank': icp.get_param('pesantren_pendaftaran.bank', default='451'),
#             'no_rekening': icp.get_param('pesantren_pendaftaran.no_rekening', default='7181863913'),
#         })
#         return res


# class SeleksiPenilaian(models.Model):
#     _name = 'seleksi.penilaian'
#     _description = 'Penilaian Seleksi Siswa Baru'

#     name            = fields.Char(string='Nama Penilaian', required=True)
#     soal_ids        = fields.One2many(comodel_name='seleksi.soal', inverse_name='penilaian_id', string='Soal Seleksi')
#     nilai           = fields.Integer(string='Nilai Seleksi', default=0)
#     penilaian_id    = fields.Many2one('seleksi.penilaian', string='Penilaian ID')  # Many2one ke penilaian lain
#     daftar_soal     = fields.Text(string='Daftar Soal', compute='_compute_daftar_soal', store=True)

#     @api.depends('soal_ids')
#     def _compute_daftar_soal(self):
#         for rec in self:
#             rec.daftar_soal = ', '.join(soal.name for soal in rec.soal_ids)

#     @api.depends('soal_ids')
#     def _compute_name(self):
#         for rec in self:
#             rec.name = 'Penilaian: ' + ', '.join(soal.name for soal in rec.soal_ids)

#     @api.onchange('soal_ids')
#     def _onchange_soal_ids(self):
#         # Mengisi penilaian_id berdasarkan soal_ids yang terpilih
#         if self.soal_ids:
#             # Ambil penilaian_id dari soal pertama yang dipilih
#             self.penilaian_id = self.soal_ids[0].penilaian_id.id


# class SoalSeleksi(models.Model):
#     _name = 'seleksi.soal'
#     _description = 'Soal untuk Seleksi Siswa Baru'

#     name            = fields.Char(string='Nama Soal', required=True)
#     active          = fields.Boolean(string='Aktif', default=True)
#     penilaian_id    = fields.Many2one(comodel_name='seleksi.penilaian', string='Penilaian', required=True)
#     nilai           = fields.Integer(string='Nilai', default=0)
#     jenjang         = fields.Selection(selection=[('sdmi','SD / MI'),('smpmts','SMP / MTS'),('smama','SMA / MA'),('smk','SMK')], string='Jenjang', required=True)
#     deskripsi       = fields.Text(string='Deskripsi Soal')

#     @api.depends('penilaian_id', 'name')
#     def _compute_name(self):
#         for record in self:
#             # Set the name of soal as the combination of penilaian and soal names
#             record.name = '%s - %s' % (record.penilaian_id.name, record.name)
            
             