from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    telegram_chat_id = fields.Char("Telegram Chat ID", help="Isi Chat ID Telegram untuk menerima notifikasi.")
