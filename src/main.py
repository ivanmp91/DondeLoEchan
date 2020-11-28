from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from justwatch import JustWatch
import ask_sdk_core.utils as ask_utils
import logging
import six

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speechText = "<say-as interpret-as=\"interjection\">Bienvenido a dónde echan cinéfilo!</say-as>, coge el mando, sientate en el sofá y disfruta!"
        rePrompt = "<say-as interpret-as=\"interjection\">Venga!</say-as>.Dime que pelicula quieres que busque, y te diré dónde puedes verla"
        return handler_input.response_builder.speak(speechText).ask(rePrompt).set_should_end_session(False).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speechText = "Bienvenidos a la ayuda de dónde echan! Sólo tienes que decirme que pelicula quieres que busque y te dire dónde puedes verla"
        return handler_input.response_builder.speak(speechText).response

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speechText = "Hasta la próxima cinefilo!."
        return handler_input.response_builder.speak(speechText).response


class SessionEndedRequestHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		return is_request_type("SessionEndedRequest")(handler_input)
	
	def handle(self, handler_input):
		handler_input.response_builder.response


class AllExceptionsHandler(AbstractExceptionHandler):
	def can_handle(self, handler_input, exception):
		return True
	
	def handle(self, handler_input, exception):
		speechText = "Lo siento, no he comprendido lo que me has dicho. Di, ayuda, para obtener más información"

		return handler_input.response_builder.speak(speechText).response

def getProviderName(provider_id):
    just_watch = JustWatch(country='ES')
    provider_details = just_watch.get_providers()
    for provider in provider_details:
        if provider['id'] == provider_id:
            return provider['clear_name']

def getFilmOffers(film):
    just_watch = JustWatch(country='ES')
    results = just_watch.search_for_item(query=film)
    if len(results['items']) > 0:
        filmOffers = results['items'][0]['offers']
        filmTitle = results['items'][0]['title']
        validOffers = []
        providers = {}
        for offer in filmOffers:
            if offer['monetization_type'] == 'flatrate':
                validOffers.append(offer)
        for offer in validOffers:
            if offer['provider_id'] not in providers:
                providers[offer['provider_id']] = getProviderName(offer['provider_id'])
        if len(providers) > 0:
            return "<say-as interpret-as=\"interjection\">Aqui lo tengo!</say-as>. {} está disponible en {}".format(filmTitle,' '.join(list(providers.values())))

    return "Lo siento, pero no he encontrado nada para {}. <say-as interpret-as=\"interjection\">Prueba con otra!</say-as>".format(film)

class GetFilmPlatform(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetFilmPlatform")(handler_input)

    def handle(self, handler_input):
        slot = ask_utils.request_util.get_slot(handler_input, "filmTitle")
        filmTitle = slot.value
        offers = getFilmOffers(filmTitle)				
        speechText = getFilmOffers(filmTitle)
        logger.info(offers)
        logger.info(speechText)

        return handler_input.response_builder.speak(speechText).response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(GetFilmPlatform())
sb.add_exception_handler(AllExceptionsHandler())

handler = sb.lambda_handler()