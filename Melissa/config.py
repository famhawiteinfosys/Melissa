class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    API_ID = "11796331"
    API_HASH = "a089161b52f234bb90a6eb915551e8c0"

    CASH_API_KEY = "P61FOF2J3CL9NH7Q"  # Get this value for currency converter from https://www.alphavantage.co/support/#api-key

    DATABASE_URL = "postgres://byrhlnok:yHaLcC5E3Ymmbx4HmFnzMJb4S2lRr2Fl@trumpet.db.elephantsql.com/byrhlnok"  # A sql database url from elephantsql.com

    EVENT_LOGS = "-1001772857132"  # Event logs channel to note down important bot level events

    MONGO_DB_URI = "mongodb+srv://IRO:IRO@cluster0.1nfrzbl.mongodb.net/?retryWrites=true&w=majority"  # Get ths value from cloud.mongodb.com

    # Telegraph link of the image which will be shown at start command.
    START_IMG = "https://i.ibb.co/jbwpmTn/Melissa-as-Cop-Girl.jpg"

    SUPPORT_CHAT = "MelissaSupport"  # Your Telegram support group chat username where your users will go and bother you

    TOKEN = "5790028102:AAHJBxd_idXLZDW6an2Km2Xux72rU0z9QO4"  # Get bot token from @BotFather on Telegram

    TIME_API_KEY = "YJIYKLP1SHTK"  # Get this value from https://timezonedb.com/api

    OWNER_ID = "6161727895"  # User id of your telegram account (Must be integer)

    # Optional fields
    BL_CHATS = []  # List of groups that you want blacklisted.
    DRAGONS = []  # User id of sudo users
    DEV_USERS = []  # User id of dev users
    DEMONS = []  # User id of support users
    TIGERS = []  # User id of tiger users
    WOLVES = []  # User id of whitelist users

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    NO_LOAD = []
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./"
    WORKERS = 8


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
