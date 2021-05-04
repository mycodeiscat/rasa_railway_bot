import json
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import dateutil.parser

from rasa_sdk.types import DomainDict

import pymorphy2

morph = pymorphy2.MorphAnalyzer(lang='uk')


# Custom action for returning all booking info as JSON
class ActionSlotsToJSON(Action):

    def name(self) -> Text:
        return "action_return_booking_info_json"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        result_dict = {'number_of_tickets': tracker.get_slot('number_of_passengers'),
                       'to': tracker.get_slot('destination_city').encode("utf-8"), 'date': tracker.get_slot('departure_date'),
                       'time': tracker.get_slot('departure_time'), 'from': tracker.get_slot('departure_city')}
        dispatcher.utter_message(text=json.dumps(result_dict))
        return []


# Custom action for validating booking form
class ValidateBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_booking_form"

    # Splitting date and time into separate slots due to DucklingExtractor shoving everything into the time slot.
    async def validate_departure_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extract date from time."""
        time_slot = tracker.get_slot('departure_time')
        date_slot = tracker.get_slot('departure_date')
        requested_slot = tracker.get_slot('requested_slot')
        date = slot_value
        datetime_obj = dateutil.parser.parse(date)
        human_date = datetime_obj.strftime('%d.%m.%Y')
        human_time = datetime_obj.strftime('%H:%M')
        if requested_slot == "departure_date":
            return {"departure_date": human_date, "departure_time": time_slot}
        if date_slot is None:
            if human_time != "00:00":  # Temporary fix
                if requested_slot != "departure_time":
                    return {"departure_date": human_date, "departure_time": human_time}
                else:
                    return {"departure_time": human_time}
            else:
                return {"departure_date": human_date, "departure_time": None}
        else:
            return {"departure_time": human_time}

    async def validate_departure_city(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        origin_slot = tracker.get_slot('departure_city')
        destination_slot = tracker.get_slot('destination_city')
        requested_slot = tracker.get_slot('requested_slot')
        normal_form = morph.parse(slot_value)[0].normal_form.capitalize()
        if requested_slot is not None:
            return {requested_slot: normal_form}
        return {"departure_city": normal_form}

    async def validate_destination_city(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        origin_slot = tracker.get_slot('departure_city')
        destination_slot = tracker.get_slot('destination_city')
        requested_slot = tracker.get_slot('requested_slot')
        normal_form = morph.parse(slot_value)[0].normal_form.capitalize()
        if requested_slot is not None:
            return {requested_slot: normal_form}
        return {"destination_city": normal_form}
