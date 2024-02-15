from typing import TYPE_CHECKING, Optional, Iterable, Union
import io
from . import send_request, Operation
from dateutil import parser
from datetime import datetime

if TYPE_CHECKING:
    from .experience import Place

class Instance():
    def __init__(self, id, data = None, place = None,
        parent = None, api_key = None) -> None:
        self.id: str = id
        self.place: Place = place
        self.name: Optional[str] = (
            data["engineInstance"]["Name"] if data else None
        )
        self.parent: Optional[Instance] = (
            parent or (Instance(data["engineInstance"]["Parent"])
            if data else None)
        )
        self.has_children: Optional[bool] = (
            data["hasChildren"] if data else None
        )
        self.__api_key = api_key

    @classmethod
    def _determine_instance_subclass(cls, data: dict):
        if not data["engineInstance"]["Details"].keys():
            instance_type = None
        else:
            instance_type = list(data["engineInstance"]["Details"].keys())[0]

        if instance_type == "Script":
            return Script
        else:
            return Instance

    def __repr__(self) -> str:
        return f"<rblxopencloud.{type(self).__name__} id=\"{self.id}\" \
name=\"{self.name}\">"
    
    def list_children(self) -> Operation[list["Instance"]]:
        _, data, _ = send_request("GET", "cloud/v2/universes/"+
            f"{self.place.experience.id}/places/{self.place.id}/instances/"+
            f"{self.id}:listChildren", authorization=self.__api_key,
            expected_status=[200])
        
        def operation_callable(response: dict):
            instance_objects = []
            
            for instance in response["instances"]:
                instance_objects.append(
                    Instance(instance["engineInstance"]["Id"], instance,
                        place=self.place, parent=self, api_key=self.__api_key)
                )

            return instance_objects

        return Operation(f"cloud/v2/{data['path']}", self.__api_key,
                         operation_callable)
    
    def _update_raw(self, instance_type: str, details: dict
        ) -> Operation[True]:
        _, data, _ = send_request("PATCH", "cloud/v2/universes/"+
            f"{self.place.experience.id}/places/{self.place.id}/instances/"+
            f"{self.id}", authorization=self.__api_key, expected_status=[200],
            json={
                "engineInstance": {
                    "Details": {
                        instance_type: details
                    }
                }
            })
        
        return Operation(f"cloud/v2/{data['path']}", self.__api_key, True)

class Script(Instance):
    def __init__(self, id, data=None, place=None,
        parent=None, api_key=None) -> None:

        details = list(data["engineInstance"]["Details"].values())[0]

        self.enabled: bool = details["Enabled"]
        self.source: str = details["Source"]

        super().__init__(id, data, place, parent, api_key)

    def update_source(self, new_source: str) -> Operation[True]:
        return self._update_raw("Script", {
            "Source": new_source
        })

InstanceType = Union[Instance, Script]
