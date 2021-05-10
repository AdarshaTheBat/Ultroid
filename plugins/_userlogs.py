# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from telethon.errors.rpcerrorlist import MediaEmptyError as mee
from telethon.utils import get_display_name

from . import *

# taglogger


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: (e.mentioned),
    ),
)
async def all_messages_catcher(e):
    if udB.get("TAG_LOG"):
        try:
            NEEDTOLOG = int(udB.get("TAG_LOG"))
        except Exception:
            return LOGS.warning("you given Wrong Grp/Channel ID in TAG_LOG.")
        x = await ultroid_bot.get_entity(e.sender_id)
        if x.bot or x.verified:
            return
        y = await ultroid_bot.get_entity(e.chat_id)
        where_n = get_display_name(y)
        who_n = get_display_name(x)
        where_l = f"https://t.me/c/{y.id}/{e.id}"
        send = await ultroid_bot.get_messages(e.chat_id, ids=e.id)
        try:
            if x.username:
                who_l = f"https://t.me/{x.username}"
                await asst.send_message(
                    NEEDTOLOG,
                    send,
                    buttons=[
                        [Button.url(who_n, who_l)],
                        [Button.url(where_n, where_l)],
                    ],
                )
            else:
                await asst.send_message(
                    NEEDTOLOG,
                    send,
                    buttons=[
                        [Button.inline(who_n, data=f"who{x.id}")],
                        [Button.url(where_n, where_l)],
                    ],
                )
        except mee:
            if x.username:
                who_l = f"https://t.me/{x.username}"
                await asst.send_message(
                    NEEDTOLOG,
                    "`Unsupported Media`",
                    buttons=[
                        [Button.url(who_n, who_l)],
                        [Button.url(where_n, where_l)],
                    ],
                )
            else:
                await asst.send_message(
                    NEEDTOLOG,
                    "`Unsupported Media`",
                    buttons=[
                        [Button.inline(who_n, data=f"who{x.id}")],
                        [Button.url(where_n, where_l)],
                    ],
                )
        except Exception as er:
            LOGS.info(str(er))
            await ultroid_bot.send_message(
                NEEDTOLOG,
                f"Please Add Your Assistant Bot - @{asst.me.username} as admin here.",
            )
    else:
        return


@callback(re.compile("who(.*)"))
async def _(e):
    wah = e.pattern_match.group(1).decode("UTF-8")
    y = await ultroid_bot.get_entity(int(wah))
    who = f"[{get_display_name(y)}](tg://user?id={y.id})"
    x = await e.reply(f"Mention By user : {who}")
    await asyncio.sleep(6)
    await x.delete()


# log for assistant
@asst.on(events.ChatAction)
async def when_asst_added_to_chat(event):
    if event.user_added:
        user = await event.get_user()
        chat = (await event.get_chat()).title
        tmp = event.added_by
        if user.id == asst.me.id:
            if int(tmp.id) == OWNER_ID or str(tmp.id) in (Redis("SUDOS").split(" ")):
                buttons = Button.inline(
                    "Leave Chat", data=f"leave_ch_{event.chat_id}|bot"
                )
                return await asst.send_message(
                    Var.LOG_CHANNEL,
                    f"#ADD_LOG\n\nSudo Users added me to {chat}.",
                    buttons=buttons,
                )
            else:
                buttons = Button.inline(
                    "Leave Chat", data=f"leave_ch_{event.chat_id}|bot"
                )
                return await asst.send_message(
                    Var.LOG_CHANNEL,
                    f"#ADD_LOG\n\n`{tmp.id}` added me to {chat}.",
                    buttons=buttons,
                )


# log for user's new joins


@ultroid.on(events.ChatAction)
async def when_ultd_added_to_chat(event):
    if event.user_added:
        user = await event.get_user()
        chat = (await event.get_chat()).title
        tmp = event.added_by
        if user.id == OWNER_ID:
            buttons = Button.inline("Leave Chat", data=f"leave_ch_{event.chat_id}|user")
            return await asst.send_message(
                Var.LOG_CHANNEL,
                f"#ADD_LOG\n\n`{tmp.id}` just added you to {chat}.",
                buttons=buttons,
            )
    elif event.user_joined:
        user = await event.get_user()
        chat = (await event.get_chat()).title
        if user.id == OWNER_ID:
            buttons = Button.inline("Leave Chat", data=f"leave_ch_{event.chat_id}|user")
            return await asst.send_message(
                Var.LOG_CHANNEL,
                f"#JOIN_LOG\n\nYou just joined {chat}.",
                buttons=buttons,
            )


@callback(
    re.compile(
        "leave_ch_(.*)",
    ),
)
@owner
async def leave_ch_at(event):
    cht = event.data_match.group(1).decode("UTF-8")
    ch_id, client = cht.split("|")
    if client == "bot":
        await asst.delete_dialog(int(ch_id))
    elif client == "user":
        await ultroid.delete_dialog(int(ch_id))
    await event.edit(f"Left `{ch_id}`")
