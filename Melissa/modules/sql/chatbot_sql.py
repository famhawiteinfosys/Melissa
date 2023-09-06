import threading

from sqlalchemy import Column, String

from Melissa.modules.sql import BASE, SESSION


class MelissaChats(BASE):
    __tablename__ = "Melissa_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


MelissaChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_Melissa(chat_id):
    try:
        chat = SESSION.query(MelissaChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_Melissa(chat_id):
    with INSERTION_LOCK:
        Melissachat = SESSION.query(MelissaChats).get(str(chat_id))
        if not Melissachat:
            Melissachat = MelissaChats(str(chat_id))
        SESSION.add(Melissachat)
        SESSION.commit()


def rem_Melissa(chat_id):
    with INSERTION_LOCK:
        Melissachat = SESSION.query(MelissaChats).get(str(chat_id))
        if Melissachat:
            SESSION.delete(Melissachat)
        SESSION.commit()
