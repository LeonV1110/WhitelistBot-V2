"""Main entry into the discordbot"""

from modules import config as cfg, discord_events, db_events
from modules.setup import create_bot, check_setup, ensure_db_driver


if __name__ == "__main__":
    if not cfg.check_config_validity():
        raise ValueError('Config file is invalid.')

    ensure_db_driver(cfg.get_db_string().split(':')[0])
    check_setup()

    db_events.init()

    bot = create_bot()
    discord_events.init(bot)
    bot.run(cfg.TOKEN)
