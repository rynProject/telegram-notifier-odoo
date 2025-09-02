import requests
from odoo import api, fields, models
from odoo.tools import format_datetime, html2plaintext


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.model and rec.res_id:
                followers = self.env["mail.followers"].search([
                    ("res_model", "=", rec.model),
                    ("res_id", "=", rec.res_id),
                ])
                partners = followers.mapped("partner_id").filtered(lambda p: p.telegram_chat_id)
                if partners:
                    bot_token = self.env['ir.config_parameter'].sudo().get_param("telegram.bot_token")
                    if bot_token:
                        record = self.env[rec.model].browse(rec.res_id)

                        # Format waktu absolute
                        date_str = format_datetime(self.env, rec.date, tz=self.env.user.tz)

                        # Status kalau ada
                        status_str = record.state if hasattr(record, "state") else ""

                        # Body plain text (supaya komentar user juga terbaca)
                        body_plain = rec.body and html2plaintext(rec.body) or ""

                        # Build message mirip chatter Odoo
                        message = (
                            f"{rec.author_id.name or 'System'}\n"
                            f"- {date_str}\n"
                            f"{record.name or ''}\n"
                            f"{status_str and '(' + status_str + ')'}\n\n"
                            f"{body_plain}"
                        ).strip()

                        for partner in partners:
                            self._send_to_telegram(bot_token, partner.telegram_chat_id, message)
        return records

    def _send_to_telegram(self, bot_token, chat_id, message):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            self.env["ir.logging"].create({
                "name": "Telegram Notification",
                "type": "server",
                "dbname": self.env.cr.dbname,
                "level": "ERROR",
                "message": str(e),
                "path": "telegram_notifier",
                "line": "0",
                "func": "_send_to_telegram",
            })
