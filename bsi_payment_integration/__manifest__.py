# -*- coding: utf-8 -*-
{
    'name': 'Pesantren BSI Payment Integration',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Integrasi Pembayaran Virtual Account Bank BSI untuk Modul Keuangan Pesantren',
    'description': """
Modul ini mengintegrasikan sistem keuangan pesantren dengan Bank Syariah Indonesia (BSI)
menggunakan webhook notifikasi pembayaran. Setelah pembayaran diterima oleh bank,
sistem akan menandai tagihan santri sebagai lunas secara otomatis.
    """,
    'author': 'Kenzo',
    'depends': ['base', 'web', 'pesantren_keuangan','pesantren_base','base_accounting_kit', 'account', 'point_of_sale','pos_wallet_odoo','hr_holidays', 'mail'], 
    'data': [     
        'security/ir.model.access.csv',        
        'views/bsi_account.xml',        
        'views/bsi_config.xml',        
    ],
    'assets': {
        'web.assets_backend': [

        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
