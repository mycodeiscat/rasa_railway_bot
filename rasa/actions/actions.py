from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# Custom action for validating and returning all booking info as JSON
class ActionSlotsToJSON(Action):

    def name(self) -> Text:
        return "action_return_booking_info_json"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        output_dict = {e['entity']: e['value'] for e in entities}
        dispatcher.utter_message(template="utter_booking_info",
                                 number=output_dict['number_of_users'],
                                 arrival_city=output_dict['arrival_city'],
                                 date=output_dict['departure_date'],
                                 time=output_dict['departure_time'],
                                 departure_city=['departure_city'])

        return []
