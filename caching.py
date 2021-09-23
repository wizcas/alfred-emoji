from peewee import *

DB_FILE = 'localcache.db'
db = SqliteDatabase(DB_FILE)


class BaseModel(Model):
    class Meta:
        database = db


class Emoji(BaseModel):
    slug = CharField(max_length=255, unique=True, index=True)
    name = CharField(max_length=255, index=True)
    emoji = CharField(max_length=3)


class Keyword(BaseModel):
    value = CharField(max_length=255, index=True)


class EmojiKeyword(BaseModel):
    emoji = ForeignKeyField(Emoji, backref='keywords')
    keyword = ForeignKeyField(Keyword, backref='emojis')


def init():
    db.connect()
    db.create_tables([Emoji, Keyword, EmojiKeyword])


def cacheEmojis(keyword, emojis):
    for emoji in emojis:
        keyword = Keyword.create(value=keyword)
        emoji = Emoji.create(
            name=emoji.name, emoji=emoji.emoji, slug=emoji.slug)
        EmojiKeyword.create(emoji=emoji, keyword=keyword)
