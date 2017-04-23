# -*- coding: utf-8 -*-
from marvinbot.utils import localized_date, get_message, trim_accents
from marvinbot.handlers import CommandHandler
from marvinbot.plugins import Plugin
from urllib import parse
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
            'base_url': 'http://api.pearson.com/v2/dictionaries/ldoce5/entries',
        }

    def configure(self, config):
        self.config = config
        pass

    def setup_handlers(self, adapter):
        self.add_handler(CommandHandler('define', self.on_define, command_description='Fetch word definition from Pearson dictionary.')
                         .add_argument('word', nargs='*', help='Word to fetch'))
        pass

    def setup_schedules(self, adapter):
        pass

    def fetch_definitions(self, word):
        # TODO: clean i[
        # base_url = 'http://api.pearson.com/v2/dictionaries/ldoce5/entries'
        # word = parse.quote_plus(word)
        params = {
            "headword": word,
            "limit": 5
        }
        response = requests.get(self.config.get('base_url'), params=params)
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
#
# {
#   "status": 200,
#   "offset": 0,
#   "limit": 10,
#   "count": 10,
#   "total": 21,
#   "url": "/v2/dictionaries/ldoce5/entries?headword=fish",
#   "results": [
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fish",
#       "homnum": 1,
#       "id": "cqAFFFCxVQ",
#       "part_of_speech": "noun",
#       "pronunciations": [
#         {
#           "audio": [
#             {
#               "lang": "British English",
#               "type": "pronunciation",
#               "url": "/v2/dictionaries/assets/ldoce/gb_pron/brelasdefish.mp3"
#             },
#             {
#               "lang": "American English",
#               "type": "pronunciation",
#               "url": "/v2/dictionaries/assets/ldoce/us_pron/fish1.mp3"
#             }
#           ],
#           "ipa": "fɪʃ"
#         }
#       ],
#       "senses": [
#         {
#           "definition": [
#             "an animal that lives in water, and uses its fins and tail to swim"
#           ],
#           "examples": [
#             {
#               "audio": [
#                 {
#                   "type": "example",
#                   "url": "/v2/dictionaries/assets/ldoce/exa_pron/p008-001688665.mp3"
#                 }
#               ],
#               "text": "Over 1,500 different species of fish inhabit the waters around the reef."
#             }
#           ],
#           "gramatical_info": {
#             "type": "countable"
#           }
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFFCxVQ"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fishing",
#       "id": "cqAFFG4XjT",
#       "part_of_speech": "noun",
#       "pronunciations": [
#         {
#           "audio": [
#             {
#               "lang": "British English",
#               "type": "pronunciation",
#               "url": "/v2/dictionaries/assets/ldoce/gb_pron/brelasdefishing.mp3"
#             },
#             {
#               "lang": "American English",
#               "type": "pronunciation",
#               "url": "/v2/dictionaries/assets/ldoce/us_pron/fishing.mp3"
#             }
#           ],
#           "ipa": "ˈfɪʃɪŋ"
#         }
#       ],
#       "senses": [
#         {
#           "collocation_examples": [
#             {
#               "collocation": "deep sea/freshwater/saltwater fishing",
#               "example": {
#                 "audio": [
#                   {
#                     "type": "example",
#                     "url": "/v2/dictionaries"
#                   }
#                 ]
#               }
#             }
#           ],
#           "cross_references": [
#             {
#               "headword": "flyfishing"
#             }
#           ],
#           "definition": [
#             "the sport or business of catching fish"
#           ],
#           "examples": [
#             {
#               "audio": [
#                 {
#                   "type": "example",
#                   "url": "/v2/dictionaries/assets/ldoce/exa_pron/p008-001260462.mp3"
#                 }
#               ],
#               "text": "Fishing is one of his hobbies."
#             }
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFG4XjT"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fish",
#       "homnum": 2,
#       "id": "cqAFFFKCmV",
#       "part_of_speech": "verb",
#       "senses": [
#         {
#           "definition": [
#             "to try to catch fish"
#           ],
#           "examples": [
#             {
#               "audio": [
#                 {
#                   "type": "example",
#                   "url": "/v2/dictionaries/assets/ldoce/exa_pron/p008-001688676.mp3"
#                 }
#               ],
#               "text": "Dad really loves to fish."
#             }
#           ],
#           "gramatical_examples": [
#             {
#               "examples": [
#                 {
#                   "audio": [
#                     {
#                       "type": "example",
#                       "url": "/v2/dictionaries/assets/ldoce/exa_pron/p008-001260297.mp3"
#                     }
#                   ],
#                   "text": "a Japanese vessel fishing for tuna in the Eastern Pacific"
#                 }
#               ],
#               "pattern": "fish for"
#             }
#           ],
#           "gramatical_info": {
#             "type": "intransitive"
#           },
#           "related_words": [
#             "fishing"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFFKCmV"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fish fry",
#       "id": "cqAFFFzkWT",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "an outdoor event held to raise money for an organization, at which fish is cooked and eaten"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFFzkWT"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fish kettle",
#       "id": "cqAFFGHRFc",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "a long deep dish used for cooking whole fish"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFGHRFc"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fish meal",
#       "id": "cqAFFGM1ET",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "dried fish crushed into a powder and put on the land to help plants grow"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFGM1ET"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary",
#         "sandbox"
#       ],
#       "headword": "bottom fishing",
#       "id": "cqAF18ND9e",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "the activity of buying shares in companies when the price is very low, and is not likely to become lower"
#           ],
#           "examples": [
#             {
#               "text": "Bottom fishing can be a risky business, because shares are usually sold cheaply for a reason."
#             }
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAF18ND9e"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "fishing tackle",
#       "id": "cqAFFGF2py",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "equipment used for fishing"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFGF2py"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary",
#         "sandbox"
#       ],
#       "headword": "coarse fishing",
#       "id": "cqAF59b3tQ",
#       "part_of_speech": "noun",
#       "senses": [
#         {
#           "definition": [
#             "the sport of catching fish, except for trout or salmon, in rivers and lakes"
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAF59b3tQ"
#     },
#     {
#       "datasets": [
#         "ldoce5",
#         "dictionary"
#       ],
#       "headword": "Fish, Michael",
#       "id": "cqAFFFNj7F",
#       "senses": [
#         {
#           "definition": [
#             "(1944–) a British weathermansomeone who gives weather reports on television and radio who works for the BBC. Many British people remember how, in 1987, he said that there would definitely not be a storm, just before the worst storm of the 20th century took place. He retired in 2004."
#           ]
#         }
#       ],
#       "url": "/v2/dictionaries/entries/cqAFFFNj7F"
#     }
#   ]
# }
