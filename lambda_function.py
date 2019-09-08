# -*- coding: utf-8 -*-

# IMPORTANT: Please note that this template uses Display Directives,
# Display Interface for your skill should be enabled through the Amazon
# developer console
# See this screen shot - https://alexa.design/enabledisplay
#TODO Aggiungi bollettini meteo https://www.arpae.it/sim/datiiningresso/Bollettino/oggi_Mattina.png
#TODO Aggiungi previsioni pioggia ogni tre ore https://www.arpae.it/sim/?mappe_numeriche/numeriche&precipitazioni

import json
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type, viewport
from ask_sdk_core.response_helper import (
    get_plain_text_content, get_rich_text_content)

from ask_sdk_model.interfaces.display import (
    ImageInstance, Image, RenderTemplateDirective, ListTemplate1,
    BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1, BodyTemplate7)
from ask_sdk_model import ui, Response
#Imports for APL interface
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    IdleCommand, AutoPageCommand, HighlightMode)

WELCOME_MESSAGE = ("Ora di': previsione radar")
HELP_MESSAGE = ("La skill mostra l'immagine del radar meteo Emilia Romagna con la previsione per le prossime tre ore. "
"Puoi guardare anche la legenda sull'immagine per capire il significato dei colori")
EXIT_SKILL_MESSAGE = ("OK")
USE_CARDS_FLAG = False
IMG_PATH = ( "https://www.arpae.it/sim/datiiningresso/Immagini/Radar/nowcast.png" ) #img size = 663x556
TITLE = "Previsione a tre ore Radar Meteo ER"
PRIMARY_TEXT = "Previsione a tre ore"
FALLBACK_ANSWER = ( "Sorry. I can't help you with that." )
APP_NAME = "RadarMeteoER"

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

def supports_display(handler_input):
    # type: (HandlerInput) -> bool
    """Check if display is supported by the skill."""
    try:
        if hasattr(
                handler_input.request_envelope.context.system.device.
                        supported_interfaces, 'display'):
            return (
                    handler_input.request_envelope.context.system.device.
                    supported_interfaces.display is not None)
    except:
        return False

def supports_APL(handler_input):
     # type: (HandlerInput) -> bool
    """Check if APL is supported by the skill."""
    try:
        if hasattr(
                handler_input.request_envelope.context.system.device.
                        supported_interfaces, 'alexa_presentation_apl'):
            return (
                    handler_input.request_envelope.context.system.device.
                    supported_interfaces.alexa_presentation_apl is not None)
    except:
        return False

# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch.
    Sample utterance: apri radar emilia romagna
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("NowcastingIntent")(handler_input) or
                is_intent_name("AMAZON.StartOverIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
#        handler_input.response_builder.speak(WELCOME_MESSAGE).ask(
#            HELP_MESSAGE)
        response_builder = handler_input.response_builder
        speech = PRIMARY_TEXT
        viewport_state = handler_input.request_envelope.context.viewport
        if not viewport_state:
            speech = "La Skill funziona solo sui device con schermo"
            response_builder.speak(speech)
            return response_builder.set_should_end_session(True).response
        response_builder.speak(speech)
        if USE_CARDS_FLAG:
            response_builder.set_card(
                ui.StandardCard(
                    title=TITLE,
                    text=PRIMARY_TEXT,
                    image=ui.Image(
                        small_image_url=IMG_PATH,
                        large_image_url=IMG_PATH,
                    )))

        if supports_display(handler_input) and not supports_APL(handler_input):
            logger.info("Supports Display")
            title = TITLE
            fg_img7 = Image(
                content_description = PRIMARY_TEXT,
                sources=[ImageInstance(
                    url=IMG_PATH
                        )])
            response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate7(
                        back_button=BackButtonBehavior.HIDDEN,
                        image=fg_img7,
                        title=title
                        )))

        if supports_APL(handler_input):
            logger.info("Supports APL")
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=APP_NAME + "_Token",
                    document=_load_apl_document("RadarMeteoAPL.json")
                )
            ).add_directive(
                ExecuteCommandsDirective(
                    token=APP_NAME + "_Token",
                    commands=[
                        IdleCommand(
                            delay=5000,
                            description="wait_5_sec")
                    ]
                )
            ).add_directive(
                ExecuteCommandsDirective(
                    token=APP_NAME + "_Token",
                    commands=[
                        IdleCommand(
                            delay=5,
                            description="last command")
                    ]
                )
            )

        return response_builder.set_should_end_session(True).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(
            handler_input.request_envelope))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.attributes_manager.session_attributes = {}
        # Resetting session

        handler_input.response_builder.speak(
            HELP_MESSAGE).ask(HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.NavigateHomeIntent")(handler_input) or
                is_intent_name("AMAZON.NavigateSettingsIntent")(handler_input) or
                is_intent_name("AMAZON.PreviousIntent")(handler_input) or
                is_intent_name("AMAZON.NextIntent")(handler_input) or
                is_intent_name("AMAZON.RepeatIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
            EXIT_SKILL_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class NowcastingIntent_handler(AbstractRequestHandler):
    """Handler for displaying the radar meteo forecast for Emilia Romagna
    Sample utterance: previsione radar
    NOTE: Moved to LaunchRequest
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("NowcastingIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NowcastingIntent")

        response_builder = handler_input.response_builder
        speech = "Previsione radar"
        viewport_state = handler_input.request_envelope.context.viewport
        if not viewport_state:
            speech = "La Skill funziona solo sui device Echo con schermo"
            response_builder.speak(speech)
            return response_builder.set_should_end_session(True).response
        response_builder.speak(speech)
        if USE_CARDS_FLAG:
            response_builder.set_card(
                ui.StandardCard(
                    title=TITLE,
                    text=PRIMARY_TEXT,
                    image=ui.Image(
                        small_image_url=IMG_PATH,
                        large_image_url=IMG_PATH,
                    )))

        if supports_display(handler_input) and not supports_APL(handler_input):
            logger.info("Supports Display")
            title = TITLE
            fg_img7 = Image(
                content_description = PRIMARY_TEXT,
                sources=[ImageInstance(
                    url=IMG_PATH
                        )])
            response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate7(
                        back_button=BackButtonBehavior.HIDDEN,
                        image=fg_img7,
                        title=title
                        )))

        if supports_APL(handler_input):
            logger.info("Supports APL")
            doc = _load_apl_document("RadarMeteoAPL.json")
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=APP_NAME + "_Token",
                    document=_load_apl_document("RadarMeteoAPL.json")
                )
            ).add_directive(
                ExecuteCommandsDirective(
                    token=APP_NAME + "_Token",
                    commands=[
                        IdleCommand(
                            delay=5000,
                            description="wait_5_sec")
                    ]
                )
            )

        return response_builder.set_should_end_session(False).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.

     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        handler_input.response_builder.speak(
            FALLBACK_ANSWER).ask(HELP_MESSAGE)

        return handler_input.response_builder.response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.
    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Mi dispiace, c'e' stato un problema."
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(NowcastingIntent_handler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()

