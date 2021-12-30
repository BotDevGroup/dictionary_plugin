# -*- coding: utf-8 -*-
from marvinbot.utils import get_message
from marvinbot.handlers import CommandHandler
from marvinbot.plugins import Plugin
from telegram import ChatAction
import logging
import requests
import re

log = logging.getLogger(__name__)

def strip_wb_format(input):
    return re.sub(r'{[^}]+}', '', input)


class DictionaryPlugin(Plugin):
    def __init__(self):
        super(DictionaryPlugin, self).__init__('dictionary_plugin')
        self.config = {}

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'wb.base_url': 'https://www.dictionaryapi.com/api/v3/references/{dictionary}/json/{word}',
            'wb.audio_url': 'https://media.merriam-webster.com/audio/prons/en/us/ogg/{subdirectory}/{audio}.ogg',
            'bighugethesaurus.base_url': 'http://words.bighugelabs.com/api/2/',
            'bighugethesaurus.api_key': None
        }

    def configure(self, config):
        self.config = config
        pass

    def setup_handlers(self, adapter):
        self.add_handler(CommandHandler('define', self.on_define,
                                        command_description='Fetch word definition from Merriam-Webster dictionary.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        self.add_handler(CommandHandler('etymology', self.on_etymology,
                                        command_description='Fetch word etymology from Merriam-Webster dictionary.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        self.add_handler(CommandHandler('pronounce', self.on_pronounce,
                                        command_description='Fetch word pronunciation from Merriam-Webster dictionary.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        self.add_handler(CommandHandler('thesaurus', self.on_thesaurus,
                                        command_description='Fetch similar words from Big Huge Thesaurus.')
                         .add_argument('word', nargs='*', help='Word to fetch'))

    def setup_schedules(self, adapter):
        pass

    def fetch_definitions(self, word):
        params = {
            "key": self.config.get("wb.api_key.collegiate")
        }
        url_params = {
            "dictionary": "collegiate",
            "word": word
        }
        url = self.config.get('wb.base_url').format(**url_params)
        response = requests.get(url, params=params)
        return response.json()

    def fetch_thesaurus(self, word):
        params = {
            'base_url': self.config.get('bighugethesaurus.base_url'),
            'api_key': self.config.get('bighugethesaurus.api_key'),
            'word': word
        }
        url = "{base_url}{api_key}/{word}/json".format(**params)
        response = requests.get(url)
        return response.json()

    def on_define(self, update, word=None, *args, **kwargs):
        message = get_message(update)
        responses = []

        word = (" ".join(word)).strip()

        if len(word) == 0:
            message.reply_text(text="❌ Word is too short.")
            return

        results = self.fetch_definitions(word)

        if len(results) == 0:
            message.reply_text(text="❌ No definitions found.")
            return

        if all([isinstance(x, str) for x in results]):
            text = "❌ Word not found.\n\nSuggestions: {suggestions}".format(suggestions=",\n".join(results[:10]))
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         text=text,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)
            return

        for result in results:
            parts = {
                "part_of_speech": result.get('fl'),
                "headword": strip_wb_format(result.get('hwi').get('hw')),
                "definition": "\n".join(["{i}. {x}".format(i=i+1, x=strip_wb_format(x)) for i, x in enumerate(result.get('shortdef'))])
            }
            response = "📖 <b>{headword}</b> (<i>{part_of_speech}</i>): {definition}".format(**parts)
            responses.append(response)

        self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                     text="\n\n".join(responses[:5]),
                                     parse_mode="HTML",
                                     disable_web_page_preview=True)

    def on_etymology(self, update, word=None, *args, **kwargs):
        message = update.effective_message
        responses = []

        word = (" ".join(word)).strip()

        if len(word) == 0:
            message.reply_text(text="❌ Word is too short.")
            return

        results = self.fetch_definitions(word)

        if len(results) == 0:
            message.reply_text(text="❌ No etymology found.")
            return

        if all([isinstance(x, str) for x in results]):
            text = "❌ Word not found.\n\nSuggestions: {suggestions}".format(suggestions=",\n".join(results[:10]))
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         text=text,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)
            return

        for result in results:
            if result.get('et') is None:
                continue
            et = [x[1] for x in result.get('et') if x[0] == "text"]
            if len(et) == 0:
                continue

            parts = {
                "date": strip_wb_format(result.get('date')),
                "headword": strip_wb_format(result.get('hwi').get('hw')),
                "etymology": "\n".join(["{i}. {x}".format(i=i+1, x=strip_wb_format(x)) for i, x in enumerate(et)])
            }
            response = "📖 <b>{headword}</b> (<i>{date}</i>): {etymology}".format(**parts)
            responses.append(response)

        if len(responses) == 0:
            message.reply_text(text="❌ No etymology found.")
            return

        self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                     text="\n\n".join(responses[:5]),
                                     parse_mode="HTML",
                                     disable_web_page_preview=True)

    def on_pronounce(self, update, word=None, *args, **kwargs):
        message = update.effective_message
        chat_id = message.chat_id

        word = (" ".join(word)).strip()

        if len(word) == 0:
            message.reply_text(text="❌ Word is too short.")
            return

        results = self.fetch_definitions(word)

        if len(results) == 0:
            message.reply_text(text="❌ No definitions found.")
            return

        if all([isinstance(x, str) for x in results]):
            text = "❌ Word not found.\n\nSuggestions: {suggestions}".format(suggestions=",\n".join(results[:10]))
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         text=text,
                                         parse_mode="HTML",
                                         disable_web_page_preview=True)
            return

        for result in results:
            hwi = result.get('hwi')
            prs = hwi.get('prs')
            for pr in prs:
                mw = pr.get('mw')
                sound = pr.get('sound')
                audio = sound.get('audio')
                if audio.startswith('bix'):
                    subdirectory = 'bix'
                elif audio.startswith('gg'):
                    subdirectory = 'gg'
                elif re.match(r'^[^a-z]', audio, re.IGNORECASE):
                    subdirectory = 'number'
                else:
                    subdirectory = audio[:1]
                url = self.config.get('wb.audio_url').format(
                    subdirectory=subdirectory,
                    audio=audio
                )
                self.adapter.bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_AUDIO)
                self.adapter.bot.sendVoice(
                    chat_id=chat_id,
                    voice=url,
                    caption=mw,
                    timeout=60,
                    reply_to_message_id=message.message_id
                )
                return

        message.reply_text(text="❌ No pronunciations found.")

    def on_thesaurus(self, update, *args, word=None, **kwargs):
        message = get_message(update)
        responses = []

        word = (" ".join(word)).strip()

        if len(word) == 0:
            message.reply_text(text="❌ Word is too short.")
            return

        data = self.fetch_thesaurus(word)

        for part_of_speech, relationships in data.items():
            responses.append("<b>{}</b>".format(part_of_speech.capitalize()))
            for relation, words in relationships.items():
                if relation == 'syn':
                    relation = 'Synonym(s)'
                elif relation == 'ant':
                    relation = 'Antonym(s)'
                elif relation == 'rel':
                    relation = 'Related word(s)'
                elif relation == 'sim':
                    relation = 'Similar word(s)'
                elif relation == 'usr':
                    relation = 'User-defined'
                response = "<i>{} {}:</i> {}".format(len(words), relation, ", ".join(words))
                responses.append(response)

        if len(responses) == 0:
            message.reply_text(text="❌ No results to show.")
            return

        self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                     text="\n".join(responses),
                                     parse_mode="HTML",
                                     disable_web_page_preview=True)
