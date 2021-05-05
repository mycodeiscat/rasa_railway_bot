import json
from typing import Any, Text, Dict, List, Optional, AnyStr

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import dateutil.parser

from rasa_sdk.types import DomainDict

import pymorphy2
import unicodedata

morph = pymorphy2.MorphAnalyzer(lang='uk')


# TODO: Read city list from file and skip morphy transformation if it's already present in list.

# Custom action for returning all booking info as JSON
class ActionSlotsToJSON(Action):

    def name(self) -> Text:
        return "action_return_booking_info_json"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """

        Args:
            tracker: contains current slot values

        Returns:
            JSONified dictionary containing booking information
        """
        result_dict = {'number_of_tickets': tracker.get_slot('number_of_passengers'),
                       'to': tracker.get_slot('destination_city'),
                       'date': tracker.get_slot('departure_date'),
                       'time': tracker.get_slot('departure_time'),
                       'from': tracker.get_slot('departure_city')}
        dispatcher.utter_message(text=json.dumps(result_dict, ensure_ascii=False))
        return []


# Custom action for validating booking form
class ValidateBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_booking_form"

    async def validate_departure_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """
        Splitting date and time into separate slots due to
        DucklingExtractor shoving everything into the time slot.
        Args:
            slot_value: time value in UTC

        Returns:
            departure_date or departure_time depending on given input.
        """
        if type(slot_value) is not str:
            slot_value = slot_value['to']

        time_slot = tracker.get_slot('departure_time')
        date_slot = tracker.get_slot('departure_date')
        requested_slot = tracker.get_slot('requested_slot')

        date = slot_value
        print(slot_value)

        datetime_obj = dateutil.parser.parse(date)
        human_date = datetime_obj.strftime('%d.%m.%Y')
        human_time = datetime_obj.strftime('%H:%M')

        if requested_slot == "departure_date":
            print("Slot_value:" + slot_value)
            print("time_slots" + time_slot)
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

    def _validate_city(self, slot_value: Any, tracker: Tracker, slot_name: Any):
        """
        City name validation
        Args:
            slot_value: city name
            tracker: entity info

        Returns:
            validated city value
        """
        if type(slot_value) is list:  # Choosing entity with highest confidence
            max_conf = 0.0
            val = ""
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == "city":
                    if entity['confidence_role'] >= max_conf and entity['role'] == slot_name:
                        max_conf = entity['confidence_role']
                        val = entity['value']
            slot_value = val

        print(slot_value)

        normal_form = morph.parse(slot_value)[0].normal_form.capitalize()
        normal_form = "Київ" if normal_form == "Кий" else normal_form  # Handling bug in pymorphy2

        return normal_form

    async def validate_departure_city(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        """
        Fill only the requested slot to avoid role confusion by NRE.
        Also used to convert city name to normal form using pymorphy2
        Args:
            slot_value: city entity

        Returns:
            destination city: official city name
        """

        requested_slot = tracker.get_slot('requested_slot')

        validated_city = self._validate_city(slot_value, tracker, "departure")

        if requested_slot is not None:
            return {requested_slot: validated_city}
        return {"departure_city": validated_city}

    async def validate_destination_city(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        """
        Fill only the requested slot to avoid role confusion by NRE.
        Also used to convert city name to normal form using pymorphy2
        Args:
            slot_value: city entity

        Returns:
            destination city: official city name
        """
        requested_slot = tracker.get_slot('requested_slot')

        validated_city = self._validate_city(slot_value, tracker, "destination")

        if requested_slot is not None:
            return {requested_slot: validated_city}
        return {"destination_city": validated_city}
