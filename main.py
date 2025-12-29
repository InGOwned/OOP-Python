from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, List

TEventArgs = TypeVar("TEventArgs")


class EventArgs:
    pass


class EventHandler(Generic[TEventArgs], ABC):
    @abstractmethod
    def handle(self, sender: Any, args: TEventArgs) -> None:
        ...


class Event(Generic[TEventArgs]):
    def __init__(self):
        self._handlers: List[EventHandler[TEventArgs]] = []

    def __iadd__(self, handler: EventHandler[TEventArgs]):
        if handler not in self._handlers:
            self._handlers.append(handler)
        return self

    def __isub__(self, handler: EventHandler[TEventArgs]):
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self

    def invoke(self, sender: Any, args: TEventArgs):
        for handler in list(self._handlers):
            handler.handle(sender, args)

    def __call__(self, sender: Any, args: TEventArgs):
        self.invoke(sender, args)


class PropertyChangedEventArgs(EventArgs):
    def __init__(self, property_name: str):
        self.property_name = property_name


class PropertyChangingEventArgs(EventArgs):
    def __init__(self, property_name: str, old_value: Any, new_value: Any):
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.can_change: bool = True


class PropertyChangedLogger(EventHandler[PropertyChangedEventArgs]):
    def handle(self, sender: Any, args: PropertyChangedEventArgs) -> None:
        print(f"[CHANGED] {sender.__class__.__name__}.{args.property_name}")


class PropertyValidator(EventHandler[PropertyChangingEventArgs]):
    def handle(self, sender: Any, args: PropertyChangingEventArgs) -> None:
        if isinstance(args.new_value, (int, float)) and args.new_value < 0:
            print(
                f"[VALIDATION] {args.property_name}: "
                f"{args.new_value} недопустимо"
            )
            args.can_change = False


class ObservableObject:
    def __init__(self):
        self.property_changing = Event[PropertyChangingEventArgs]()
        self.property_changed = Event[PropertyChangedEventArgs]()

    def _set_property(self, name: str, value: Any):
        old_value = getattr(self, name)

        changing_args = PropertyChangingEventArgs(
            name, old_value, value
        )
        self.property_changing(self, changing_args)

        if not changing_args.can_change:
            return

        setattr(self, name, value)
        self.property_changed(
            self, PropertyChangedEventArgs(name)
        )


class Person(ObservableObject):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__()
        self._name = name
        self._age = age
        self._salary = salary

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._set_property("_name", value)

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._set_property("_age", value)

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):
        self._set_property("_salary", value)


class Product(ObservableObject):
    def __init__(self, title: str, price: float, quantity: int):
        super().__init__()
        self._title = title
        self._price = price
        self._quantity = quantity

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._set_property("_title", value)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._set_property("_price", value)

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._set_property("_quantity", value)


if __name__ == "__main__":
    logger = PropertyChangedLogger()
    validator = PropertyValidator()

    person = Person("Alex", 20, 50000)
    person.property_changed += logger
    person.property_changing += validator

    person.age = 30
    person.salary = -100

    product = Product("Laptop", 1200, 5)
    product.property_changed += logger
    product.property_changing += validator

    product.price = 1500
    product.quantity = -2
