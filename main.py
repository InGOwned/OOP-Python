from typing import Any, Generic, TypeVar, List
from abc import ABC, abstractmethod

TEventArgs = TypeVar("TEventArgs")


class EventArgs:
    pass


class EventHandler(Generic[TEventArgs], ABC):
    @abstractmethod
    def handle(self, sender: Any, args: TEventArgs) -> None:
        pass


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
        for h in list(self._handlers):
            h.handle(sender, args)

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


class ObservableProperty:
    def __init__(self, name: str, default: Any = None):
        self.name = name
        self.private_name = f"_{name}"
        self.default = default

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, value):
        old_value = getattr(obj, self.private_name, self.default)

        changing_args = PropertyChangingEventArgs(
            self.name, old_value, value
        )
        obj.property_changing(obj, changing_args)

        if not changing_args.can_change:
            return

        setattr(obj, self.private_name, value)
        obj.property_changed(
            obj, PropertyChangedEventArgs(self.name)
        )


class ObservableObject:
    def __init__(self):
        self.property_changing = Event[PropertyChangingEventArgs]()
        self.property_changed = Event[PropertyChangedEventArgs]()


class Person(ObservableObject):
    name = ObservableProperty("name")
    age = ObservableProperty("age")
    salary = ObservableProperty("salary")

    def __init__(self, name: str, age: int, salary: float):
        super().__init__()
        self.name = name
        self.age = age
        self.salary = salary


class Product(ObservableObject):
    title = ObservableProperty("title")
    price = ObservableProperty("price")
    quantity = ObservableProperty("quantity")

    def __init__(self, title: str, price: float, quantity: int):
        super().__init__()
        self.title = title
        self.price = price
        self.quantity = quantity


if __name__ == "__main__":
    logger = PropertyChangedLogger()
    validator = PropertyValidator()

    person = Person("Alex", 20, 50000)
    person.property_changed += logger
    person.property_changing += validator

    person.age = 30
    person.salary = -100  # отмена

    product = Product("Laptop", 1200, 5)
    product.property_changed += logger
    product.property_changing += validator

    product.price = 1500
    product.quantity = -2  # отмена
