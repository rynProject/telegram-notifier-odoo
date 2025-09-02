{
    "name": "Telegram Notifier",
    "version": "16.0.1.0.0",
    "summary": "Send chatter notifications to Telegram followers",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "views/res_partner_view.xml",
        "views/telegram_settings_view.xml",
    ],
    "application": False,
    "installable": True,
    "controllers": ["controllers/telegram_webhook.py"],
}
