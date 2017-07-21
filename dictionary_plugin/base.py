# -*- coding: utf-8 -*-
from marvinbot.utils import get_message
from marvinbot.handlers import CommandHandler
from marvinbot.plugins import Plugin
import logging
import requests

log = logging.getLogger(__name__)


class DictionaryPlugin(Plugin):
    def __init__(self):
        super(DictionaryPlugin, self).__init__('dictionary_plugin')
        self.config = {}

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'pearson_base_url': 'http://api.pearson.com/v2/dictionaries/ldoce5/entries',
            'bighugethesaurus_base_url': 'http://words.bighugelabs.com/api/2/',
            'bighugethesaurus_api_key': None
        }

    def configure(self, config):
        self.config = config
        pass

    def setup_handlers(self, adapter):
        self.add_handler(CommandHandler('define', self.on_define, command_description='Fetch word definition from Pearson dictionary.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        self.add_handler(CommandHandler('thesaurus', self.on_thesaurus,
                                        command_description='Fetch similar words from Big Huge Thesaurus.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        pass

    def setup_schedules(self, adapter):
        pass

    def fetch_definitions(self, word):
        params = {
            "headword": word,
            "limit": 5
        }
        response = requests.get(self.config.get('pearson_base_url'), params=params)
        return response.json()

    def fetch_thesaurus(self, word):
        params = {
            'base_url':  self.config.get('bighugethesaurus_base_url'),
            'api_key': self.config.get('bighugethesaurus_api_key'),
            'word': word
        }
        url = "{base_url}{api_key}/{word}/json".format(**params)
        response = requests.get(url)
        return response.json()

    def on_define(self, update, *args, word=None, **kwargs):
        message = get_message(update)
        responses = []

        word = (" ".join(word)).strip()

        if len(word)==0:
            message.reply_text(text="❌ Word is too short.")
            return

        data = self.fetch_definitions(word)

        results = data.get('results')

        count = data.get('count')
        if count == 0:
            message.reply_text(text="❌ No definitions found.")
            return

        for result in results:
            part_of_speech = result.get('part_of_speech')
            headword = result.get('headword')

            # Skip results that are not part of speech
            if part_of_speech is None:
                continue

            senses = result.get('senses')

            # Skip result without sense
            if senses is None:
                continue

            definition = [sense.get('definition')[0] for sense in senses if sense.get('definition') is not None][0]

            response = "📖 <b>{headword}</b> (<i>{part_of_speech}</i>): {definition}".format(headword=headword, part_of_speech=part_of_speech, definition=definition)
            responses.append(response)

        if len(responses)==0:
            message.reply_text(text="❌ There were results, but no proper definitions found.")
            return


        self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                text="\n\n".join(responses),
                                parse_mode="HTML",
                                disable_web_page_preview=True)

    def on_thesaurus(self, update, *args, word=None, **kwargs):
        message = get_message(update)
        responses = []

        word = (" ".join(word)).strip()

        if len(word)==0:
            message.reply_text(text="❌ Word is too short.")
            return

        data = self.fetch_thesaurus(word)

        for part_of_speech,relationships in data.items():
            responses.append("<b>{}</b>".format(part_of_speech.capitalize()))
            for relation,words in relationships.items():
                if relation=='syn':
                    relation = 'Synonym(s)'
                elif relation=='ant':
                    relation = 'Antonym(s)'
                elif relation=='rel':
                    relation = 'Related word(s)'
                elif relation=='sim':
                    relation = 'Similar word(s)'
                elif relation=='usr':
                    relation = 'User-defined'
                response = "<i>{} {}:</i> {}".format(len(words),relation,", ".join(words))
                responses.append(response)


        if len(responses) == 0:
            message.reply_text(text="❌ No results to show.")
            return

        self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="\n".join(responses),
                                 parse_mode="HTML",
                                 disable_web_page_preview=True)
