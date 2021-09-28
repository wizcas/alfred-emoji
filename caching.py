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
    value = CharField(max_length=255, unique=True, index=True)


class EmojiKeyword(BaseModel):
    emoji = ForeignKeyField(Emoji, backref='keywords')
    keyword = ForeignKeyField(Keyword, backref='emojis')

    class Meta:
        indexes = (
            (('emoji', 'keyword'), True),
        )


def init():
    db.connect()
    db.create_tables([Emoji, Keyword, EmojiKeyword])


def cacheEmojis(keyword, emojis):
    keyword = __upsert(lambda: Keyword.get(Keyword.value == keyword),
                       lambda: Keyword.create(value=keyword))
    for emoji in emojis:
        emoji = __upsert(
            lambda: Emoji.get(Emoji.slug == emoji.slug),
            lambda: Emoji.create(
                name=emoji.name, emoji=emoji.emoji, slug=emoji.slug))
        (EmojiKeyword.insert(emoji=emoji, keyword=keyword)
         .on_conflict_ignore()
         .execute())


def findEmojis(keyword):
    try:
        emojis = []
        emojiIds = EmojiKeyword.select(EmojiKeyword.emoji).join(
            Keyword).where(Keyword.value == keyword)

        query = Emoji.select().where(Emoji.id.in_(emojiIds))
        for result in query.execute():
            emojis.append(result)
        return emojis if len(emojis) > 0 else None
    except DoesNotExist:
        return None


def __upsert(getter, creator):
    try:
        return getter()
    except DoesNotExist:
        return creator()
