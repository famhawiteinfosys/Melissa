import importlib
import re
import time
from platform import python_version as y
from sys import argv

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import Melissa.modules.sql.users_sql as sql
from Melissa import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from Melissa.modules import ALL_MODULES
from Melissa.modules.helper_funcs.chat_status import is_user_admin
from Melissa.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

start_txt = """
ʜᴇʏ BABY🥀 `{}`, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ❣️!!
"""
DONATION_LINK = "Aside"

PM_START_TEXT = """
*Hello BABY {} !*
» *ɪ'ᴍ {BOT_NAME} !* 🫧 [🥀](https://i.ibb.co/jbwpmTn/Melissa-as-Cop-Girl.jpg) ᴀ ᴘᴏᴡᴇʀꜰᴜʟ MUSIC + ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ 
────────────────────────
× *✨Uptime🥀:* `{}`
× `{}` *✨users, ✨across🥀* `{}` *chats.*
────────────────────────
» ʜɪᴛ /help ᴛᴏ ꜱᴇᴇ ᴍʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ.
"""

buttons = [
        [
        InlineKeyboardButton(
            text="Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ],
    [
        InlineKeyboardButton(text="Command", callback_data="Melissa_"),
    ],
    [
        InlineKeyboardButton(text="About", callback_data="Melissa_admin"),
        InlineKeyboardButton(text="Owner", url=f"tg://user?id={OWNER_ID}"),
    ],
    [
        InlineKeyboardButton(text="Support", url="https://t.me/MelissaUpdates"),
        InlineKeyboardButton(text="Updates", url="https://t.me/MelissaUpdates"),
    ],
]


HELP_STRINGS = f"""
*» {BOT_NAME} ᴄᴏᴍᴍᴀɴᴅs ᴀᴠᴀɪʟᴀʙʟᴇ:*
» /help: PM's ʏᴏᴜ ᴛʜɪs ᴍᴇssᴀɢᴇ.
» /donate: ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴏɴ ʜᴏᴡ ᴛᴏ ᴅᴏɴᴀᴛᴇ!
» /settings:
   ↣ ɪɴ ᴘᴍ: ᴡɪʟʟ sᴇɴᴅ ʏᴏᴜ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ғᴏʀ ᴀʟʟ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs.
   ↣ ɪɴ ᴀ ɢʀᴏᴜᴘ: ᴡɪʟʟ ʀᴇᴅɪʀᴇᴄᴛ ʏᴏᴜ ᴛᴏ ᴘᴍ, ᴡɪᴛʜ ᴀʟʟ ᴛʜᴀᴛ ᴄʜᴀᴛ  sᴇᴛᴛɪɴɢs.
"""


DONATE_STRING = """ᴊᴜsᴛ sᴜᴘᴘᴏʀᴛ ᴜs"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}


for module_name in ALL_MODULES:
    imported_module = importlib.import_module(f"Melissa.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("ᴄᴀɴ'ᴛ ʜᴀᴠᴇ ᴛᴡᴏ ᴍᴏᴅᴜʟᴇs ᴡɪᴛʜ ᴛʜᴇ sᴀᴍᴇ ɴᴀᴍᴇ! ᴘʟᴇᴀsᴇ ᴄʜᴀɴɢᴇ ᴏɴᴇ")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("ᴛʜɪs ᴘᴇʀsᴏɴ ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇssᴀɢᴇ")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    usr = update.effective_user
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if mod == "Admins":
                    mod = "Admins"
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Back", callback_data="help_back"
                                )
                            ]
                        ]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match[1])

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match[1], update.effective_user.id, False)
                else:
                    send_settings(match[1], update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            lel = update.effective_message.reply_text(
                start_txt.format(usr.first_name), parse_mode=ParseMode.MARKDOWN
            )
            time.sleep(1.2)
            lel.edit_text(f"ᴡᴀɪᴛ ʙᴀʙʏ🖤! ʟᴇᴛ ᴍᴇ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ \nꜱᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴍʏ ᴘᴏᴡᴇʀ✨❣️🥀")
            time.sleep(1.2)
            lel.delete()
            K = update.effective_message.reply_sticker(
                "CAACAgUAAxkBAAIMUGO8z_kVv8pE_UPT0xRQDKa5BYn0AAI9CQACFm7gVI4RHTP_GrcvLQQ"
            )
            time.sleep(1.2)
            K.delete()
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats(),
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ʜᴇʏ BABY❣️🥀 `{}`,\n\n✨ ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ !\n➥ᴜᴘᴛɪᴍᴇ✨: `{}` \n➥ᴜsᴇʀs🥀: `{}` \n➥ᴄʜᴀᴛs❣️: `{}` ".format(
                usr.first_name,
                uptime,
                sql.num_users(),
                sql.num_chats(),
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🫧ꜱᴜᴘᴘᴏʀT🫧",
                            url=f"https://t.me/Melissasupport",
                        ),
                        InlineKeyboardButton(
                            text="Updates",
                            url=f"https://t.me/MelissaUpdates",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="❣️ᴏᴡɴᴇʀ❣️",
                            url=f"tg://user?id={OWNER_ID}",
                        ),
                        InlineKeyboardButton(
                            text="✨ᴄʟᴏsᴇ✨",
                            callback_data="close_",
                        ),
                    ],
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ʜᴇʟᴘ ꜰᴏʀ ᴛʜA ✨ *{}* ᴍᴏᴅᴜʟᴇ:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def Melissa_about_callback(update, context):
    query = update.callback_query
    if query.data == "Melissa_":
        query.message.edit_text(
            text="✨🥀❣️ *I'm {} !*, a powerful group management + music bot built to help you manage your group easily."
            "\n\n Click on button bellow to get basic help for *{} !*.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="🎵ᴍᴜꜱɪᴄ🥀", callback_data="Melissa_supports"),
                    InlineKeyboardButton(text="⚙️ᴍᴀɴᴀɢᴇᴍᴇɴT🥀", callback_data="help_back"),
                 ],
                 [
                    InlineKeyboardButton(text="◁", callback_data="Melissa_back"),
                 ]
                ]
            ),
        )
    elif query.data == "Melissa_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
            PM_START_TEXT.format(
                escape_markdown(first_name),
                escape_markdown(uptime),
                sql.num_users(),
                sql.num_chats(),
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )

    elif query.data == "Melissa_admin":
        query.message.edit_text(
            text=f"*✨ I'm {BOT_NAME}, ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ʙᴏᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ.*"
            "\n» ɪ ᴄᴀɴ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ."
            "\n» ɪ ᴀᴍ ʙᴜɪʟᴛ ᴡɪᴛʜ [ᴘʏᴛʜᴏɴ](https://www.python.org/) ,[ᴍᴏɴɢᴏᴅʙ](https://www.mongodb.com/)."
            "\n» ᴍʏ ʙᴀꜱᴇ ɪꜱ ᴍᴀᴅᴇ ᴜᴘ ᴏꜰ [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon) ᴀɴᴅ [ᴘʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)."
            "\n» ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ꜱʏꜱᴛᴇᴍ."
            "\n» ɪ ʜᴀᴠᴇ ɴꜱᴡꜰ ᴛᴏ ᴅᴇᴛᴇᴄᴛ ᴀᴅᴜʟᴛ ᴄᴏɴᴛᴇɴᴛꜱ ᴀɴᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ᴘᴏʀɴᴏɢʀᴀᴘʜɪᴄ ᴄᴏɴᴛᴇɴᴛꜱ."
            "\n» ɪ ᴄᴀɴ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴘᴀᴍꜱ ᴀɴᴅ ʀᴀɪᴅꜱ."
            "\n» ɪ ʜᴀᴠᴇ ᴍᴀɴʏ ᴛᴏᴏʟꜱ ꜰᴏʀ ꜰᴜɴ ᴀɴᴅ ᴇɴᴊᴏʏᴍᴇɴᴛ ᴛᴏ ᴇɴᴛᴇʀᴛᴀɪɴ ʏᴏᴜ ᴀʟʟ"
            "\n» ɪ ᴀᴍ ᴘᴜʙʟɪꜱʜᴇᴅ ᴜɴᴅᴇʀ ʟɪᴄᴇɴꜱᴇ :- [ɢɴᴜ ʟɪᴄᴇɴꜱᴇ](https://t.me/shaeep43)"
            "\n\n ᴛʜᴀɴᴋs ғᴏʀ sᴜᴘᴘᴏʀᴛɪɴɢ ᴜs",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="Melissa_back")]]
            ),
        )

    elif query.data == "Melissa_notes":
        query.message.edit_text(
            text=f"<b>✨ ᴜꜱᴇʀ~ᴄᴏᴍᴍᴀɴᴅꜱ</b>"
            f"\n\n» /play : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
            f"\n» /vplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴠɪᴅᴇᴏ-ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
            f"\n» /cplay : ꜱᴛᴀʀᴛꜱ ᴘʟᴀʏɪɴɢ ɢɪᴠᴇɴ ᴛʀᴀᴄᴋ ɪɴ ᴄʜᴀɴɴᴇʟ"
            f"\n» /loop [ᴅɪsᴀʙʟᴇ/ᴇɴᴀʙʟᴇ] ᴏʀ [ʙᴇᴛᴡᴇᴇɴ 1:10] : ᴡʜᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ʙᴏᴛ ᴡɪʟʟ ᴩʟᴀʏ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ɪɴ ʟᴏᴏᴩ ғᴏʀ 10 ᴛɪᴍᴇs ᴏʀ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ʀᴇǫᴜᴇsᴛᴇᴅ ʟᴏᴏᴩs."
            f"\n» /shuffle : sʜᴜғғʟᴇ ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs."
            f"\n» /seek : sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ."
            f"\n» /seekback : ʙᴀᴄᴋᴡᴀʀᴅ sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ."
            f"\n» /song - ᴛᴏ ɢᴇᴛ ᴛʜᴇ ꜱᴏɴɢ ᴀᴜᴅɪᴏ"
            f"\n» /lyrics [sᴏɴɢ ɴᴀᴍᴇ] : sᴇᴀʀᴄʜ ʟʏʀɪᴄs ғᴏʀ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ sᴏɴɢ ᴀɴᴅ sᴇɴᴅ ᴛʜᴇ ʀᴇsᴜʟᴛs.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="Melissa_supports")]]
            ),
        )
    elif query.data == "Melissa_supports":
        query.message.edit_text(
            text="*✨ʜᴇʏ ᴛʜɪs ɪs {BOT_NAME}, ᴍᴜꜱɪᴄ ᴄᴏᴍᴍᴀɴᴅ*"
            "\n\nʜᴇʀᴇ ɪꜱ {BOT_NAME}, ᴍᴜꜱɪᴄ ᴄᴏᴍᴍᴀɴᴅ ᴄʜᴏᴏꜱᴇ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ɴᴇᴇᴅꜱ.\n\nᴛʜᴀɴᴋ ʏᴏᴜ",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="✨ᴜꜱᴇʀ✨", callback_data="Melissa_notes"),
                    InlineKeyboardButton(text="✨ᴀᴅᴍɪɴ✨", callback_data="Melissa_credit"),
                 ],
                                  [
                    InlineKeyboardButton(text="❣️ꜱᴜᴅᴏ❣️", callback_data="source_"),
                 
                 ],
                 [
                    InlineKeyboardButton(text="◁", callback_data="Melissa_"),
                 
                 ]
                ]
            ),
        )


    elif query.data == "Melissa_credit":
        query.message.edit_text(
            text=f"<b>✨ ᴀᴅᴍɪɴ~ᴄᴏᴍᴍᴀɴᴅs</b>"
            f"\n ɴᴏᴛᴇ : ᴊᴜsᴛ ᴀᴅᴅ **ᴄ** ɪɴ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴜsᴇ ᴛʜᴇᴍ ғᴏʀ ᴄʜᴀɴɴᴇʟ."
            f"\n\n» /pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."
            f"\n» /resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."
            f"\n» /skip : sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."
            f"\n» /end ᴏʀ /stop : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."
            f"\n» /player : ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ."
            f"\n» /queue : sʜᴏᴡs ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ʟɪsᴛ."
            f"\n» /auth [ᴜsᴇʀɴᴀᴍᴇ] : ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ ᴀᴜᴛʜ ʟɪsᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ."
            f"\n» /unauth [ᴜsᴇʀɴᴀᴍᴇ] : ʀᴇᴍᴏᴠᴇ ᴀ ᴀᴜᴛʜ ᴜsᴇʀs ғʀᴏᴍ ᴛʜᴇ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ."
            f"\n» /authusers : sʜᴏᴡs ᴛʜᴇ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴩ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="◁", callback_data="Melissa_supports"),
                 ]
                ]
            ),
        )

def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=f"<b>✨ sᴜᴅᴏ~ᴄᴏᴍᴍᴀɴᴅs</b>"
            f"\n\n» /blacklistchat [ᴄʜᴀᴛ ɪᴅ] : ʙʟᴀᴄᴋʟɪsᴛ ᴀ ᴄʜᴀᴛ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ."
            f"\n» /whitelistchat [ᴄʜᴀᴛ ɪᴅ] : ᴡʜɪᴛᴇʟɪsᴛ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛ."
            f"\n» /blacklistedchat : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴄʜᴀᴛs."
            f"\n» /block [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴄʜᴜᴛɪʏᴀ] : sᴛᴀʀᴛs ɪɢɴᴏʀɪɴɢ ᴛʜᴇ ᴄʜᴜᴛɪʏᴀ, sᴏ ᴛʜᴀᴛ ʜᴇ ᴄᴀɴ'ᴛ ᴜsᴇ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs."
            f"\n» /unblock [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] : ᴜɴʙʟᴏᴄᴋs ᴛʜᴇ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀ."
            f"\n» /blockedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs."
            f"\n» /get_log [ɴᴜᴍʙᴇʀ ᴏғ ʟɪɴᴇs] : ɢᴇᴛ ʟᴏɢs ᴏғ ʏᴏᴜʀ ʙᴏᴛ [ᴅᴇғᴀᴜʟᴛ ᴠᴀʟᴜᴇ ɪs 100 ʟɪɴᴇs]"
            f"\n» /logger [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ʙᴏᴛ ᴡɪʟʟ sᴛᴀʀᴛ ʟᴏɢɢɪɴɢ ᴛʜᴇ ᴀᴄᴛɪᴠɪᴛɪᴇs ʜᴀᴩᴩᴇɴ ᴏɴ ʙᴏᴛ."
            f"\n» /restart : ʀᴇsᴛᴀʀᴛs ʏᴏᴜʀ ʙᴏᴛ.",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="◁", callback_data="Melissa_supports")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ʜᴇʟᴘ",
                                url="https://t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "» ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʜᴇʟᴩ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴏᴩᴇɴ ʜᴇʀᴇ",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* ʜᴀꜱ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇ:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
        "ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ Qᴜɪᴛᴇ ᴀ ꜰᴇᴡ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {} - ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ "
                "ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇꜱᴛᴇᴅ ɪɴ.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ɴᴏᴛ ᴍᴏᴅɪꜰɪᴇᴅ",
            "Qᴜᴇʀʏ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
            "ᴍᴇꜱꜱᴀɢᴇ ᴄᴀɴ'ᴛ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ",
        ]:
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ ɪɴ ꜱᴇᴛᴛɪɴɢꜱ ʙᴜᴛᴛᴏɴꜱ. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪꜱ ᴄʜᴀᴛ'ꜱ ꜱᴇᴛᴛɪɴɢꜱ, ᴀꜱ ᴡᴇʟʟ ᴀꜱ ʏᴏᴜʀꜱ."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="✨ꜱᴇᴛᴛɪɴɢꜱ✨",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ BABY."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 5518757491:
            update.effective_message.reply_text(
                "ɪ'ᴍ ꜰʀᴇᴇ ꜰᴏʀ ᴇᴠᴇʀʏᴏɴᴇ 🖤 ɪꜰ ʏᴏᴜ ᴡᴀɴɴᴀ ᴍᴀᴋᴇ ᴍᴇ ꜱᴍɪʟᴇ, ᴊᴜꜱᴛ ᴊᴏɪɴ"
                "[My Channel]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "ɪ'ᴠᴇ ᴘᴍ'ᴇᴅ ʏᴏᴜ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪɴɢ ᴛᴏ ᴍʏ ᴄʀᴇᴀᴛᴏʀ!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ꜰɪʀꜱᴛ ᴛᴏ ɢᴇᴛ ᴅᴏɴᴀᴛɪᴏɴ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("ᴍɪɢʀᴀᴛɪɴɢ ꜰʀᴏᴍ %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴍɪɢʀᴀᴛᴇᴅ!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendAnimation(
                f"@{SUPPORT_CHAT}",
                animation="https://te.legra.ph/file/76242492a4a2d080875af.mp4",
                caption=f"""
ㅤ{dispatcher.bot.first_name} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ .....
━━━━━━━━━━━━━
» **✨ ᴏᴡɴᴇʀ ❣️ :** [Pi͢͢͢kสcђu♡](https://t.me/shaeep43)
» **🥀 ʟɪʙʀᴀʀʏ 🥀  :** `{telever}`
» **🥀 ᴛᴇʟᴇᴛʜᴏɴ 🥀 :** `{tlhver}`
» **🥀 ᴘʏʀᴏɢʀᴀᴍ 🥀 :** `{pyrover}`
» **🥀 ᴍᴏɴɢᴏ ᴅʙ 🥀 :** `3.9.0`
» **🥀 ꜱǫʟᴀʟᴄʜᴇᴍʏ 🥀 :** `1.4.31`
━━━━━━━━━━━━━

✨🥀❣️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ 🥀 : [🇮 🇷 🇴 ](https://t.me/MelissaUpdates)

""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                "ʙᴏᴛ ɪsɴᴛ ᴀʙʟᴇ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ support_chat, ɢᴏ ᴀɴᴅ ᴄʜᴇᴄᴋ !"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        Melissa_about_callback, pattern=r"Melissa_", run_async=True
    )

    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(
        Filters.status_update.migrate, migrate_chats, run_async=True
    )

    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
