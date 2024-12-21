from django.core.cache import cache

from config.settings import CACHE_ENABLED
from mail_serv.models import Mailing, MessageManagement, Recipient


def get_recipients_from_cache():
    '''Получает список всех получателей из кэша, если кэширование включено.'''
    if not CACHE_ENABLED:
        return Recipient.objects.all()
    key = "recipients"
    recip = cache.get(key)
    if recip is not None:
        return recip
    recip = Recipient.objects.all()
    cache.set(key, recip)
    return recip


def get_messages_from_cache():
    '''Получает список всех сообщений из кэша, если кэширование включено.'''
    if not CACHE_ENABLED:
        return MessageManagement.objects.all()
    key = "messages"
    message = cache.get(key)
    if message is not None:
        return message
    message = MessageManagement.objects.all()
    cache.set(key, message)
    return message


def get_mailings_from_cache():
    '''Получает список всех рассылок из кэша, если кэширование включено.'''
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailings"
    mail = cache.get(key)
    if mail is not None:
        return mail
    mail = Mailing.objects.all()
    cache.set(key, mail)
    return mail
