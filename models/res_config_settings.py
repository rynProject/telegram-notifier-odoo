from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    telegram_bot_token = fields.Char(
        string="Telegram Bot Token",
        config_parameter="telegram.bot_token",
        help="Token bot Telegram untuk kirim notifikasi."
    )
