from odoo import fields, models

class BsiConfig(models.Model):
    _name = "bsi.api.config"
    _description = "Konfigurasi API BSI"

    name = fields.Char(default="Konfigurasi BSI")
    client_id = fields.Char(string="Client ID")  
    secret_key = fields.Char(string="Secret Key")  
    api_key = fields.Char(string="API Key")
    base_url = fields.Char(string="URL API", default="https://api.bsi.co.id")
    callback_url = fields.Char(string="Webhook Callback URL")
    is_sandbox = fields.Boolean(string="Mode Sandbox", default=True)
