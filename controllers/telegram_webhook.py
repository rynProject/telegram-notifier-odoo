from odoo import http
from odoo.http import request

class TelegramWebhook(http.Controller):

    @http.route('/telegram/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def telegram_webhook(self, **post):
        data = request.jsonrequest
        if not data:
            return {"ok": False}

        message = data.get("message")
        if not message:
            return {"ok": False}

        chat_id = message["chat"]["id"]

        # Kalau user share nomor HP
        if "contact" in message:
            phone = message["contact"].get("phone_number")
            if phone:
                # Normalisasi nomor HP (misalnya +62)
                phone = phone.replace(" ", "").replace("-", "")
                partner = request.env["res.partner"].sudo().search([
                    "|",
                    ("mobile", "like", phone),
                    ("phone", "like", phone),
                ], limit=1)
                if partner:
                    partner.sudo().write({"telegram_chat_id": chat_id})
                else:
                    # opsional: auto-create partner baru
                    request.env["res.partner"].sudo().create({
                        "name": message["contact"].get("first_name") or "Telegram User",
                        "mobile": phone,
                        "telegram_chat_id": chat_id,
                    })
            return {"ok": True}

        # Kalau user ketik /start → minta share nomor HP
        if message.get("text") == "/start":
            bot_token = request.env['ir.config_parameter'].sudo().get_param("telegram.bot_token")
            if bot_token:
                import requests as req
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "Halo, silakan share nomor HP Anda untuk aktivasi notifikasi.",
                    "reply_markup": {
                        "keyboard": [[{
                            "text": "Bagikan Nomor HP 📱",
                            "request_contact": True
                        }]],
                        "one_time_keyboard": True,
                        "resize_keyboard": True,
                    }
                }
                req.post(url, json=payload, timeout=10)

        return {"ok": True}
