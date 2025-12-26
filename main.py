from math import pi

class Angle:
    def __init__(self, angle: float, unit: str='radians') -> None:
        if unit == 'degrees':
            self._radians = (angle % 360) * pi / 180
        else:
            self._radians = angle % (2 * pi)

    @property
    def degrees(self) -> float:
        return (self._radians * 180 / pi) % 360

    @degrees.setter
    def degrees(self, value: float) -> None:
        self._radians = (value % 360) * pi / 180

    @property
    def radians(self) -> float:
        return self._radians

    @radians.setter
    def radians(self, value: float) -> None:
        self._radians = value % (2 * pi)

    def __float__(self) -> float:
        return self._radians

    def __int__(self) -> int:
        return int(self._radians)

    def __str__(self) -> str:
        return f"{self.degrees:.2f}° ({self._radians:.4f} rad)"

    def __repr__(self) -> str:
        return f"Angle({self._radians})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Angle):
            return abs(self._radians - other._radians) < 1e-10
        elif isinstance(other, (int, float)):
            return abs(self._radians - other) < 1e-10
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, Angle):
            return self._radians < other._radians
        elif isinstance(other, (int, float)):
            return self._radians < other
        return NotImplemented

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __gt__(self, other) -> bool:
        return not (self <= other)

    def __ge__(self, other) -> bool:
        return not (self < other)

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians + other._radians, 'radians')
        elif isinstance(other, (int, float)):
            return Angle(self._radians + other, 'radians')
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians - other._radians, 'radians')
        elif isinstance(other, (int, float)):
            return Angle(self._radians - other, 'radians')
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Angle(other - self._radians, 'radians')
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Angle(self._radians * other, 'radians')
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)) and other != 0:
            return Angle(self._radians / other, 'radians')
        raise ValueError("Division by zero")

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return Angle(other / self._radians, 'radians')
        return NotImplemented

class AngleRange:
    def __init__(self, start, end, include_start: bool = True, include_end: bool = True):
        if isinstance(start, (int, float)):
            start = Angle(start, 'radians')
        if isinstance(end, (int, float)):
            end = Angle(end, 'radians')
        
        if not isinstance(start, Angle) or not isinstance(end, Angle):
            raise TypeError("Start and end must be angles, floats, or ints")
        
        self.start = start
        self.end = end
        self.include_start = include_start
        self.include_end = include_end

    def __str__(self) -> str:
        start_char = "[" if self.include_start else "("
        end_char = "]" if self.include_end else ")"
        return f"{start_char}{self.start}, {self.end}{end_char}"

    def __repr__(self) -> str:
        return f"AngleRange({repr(self.start)}, {repr(self.end)}, {self.include_start}, {self.include_end})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return False
        return (self.start == other.start and 
                self.end == other.end and 
                self.include_start == other.include_start and 
                self.include_end == other.include_end)

    def length(self) -> float:
        diff = self.end._radians - self.start._radians
        if diff < 0:
            diff += 2 * pi
        return diff

    def __abs__(self):
        return self.length()

    def __contains__(self, item) -> bool:
        if isinstance(item, Angle):
            angle_rad = item._radians
            start_rad = self.start._radians
            end_rad = self.end._radians
            
            if start_rad <= end_rad:
                if self.include_start and self.include_end:
                    return start_rad <= angle_rad <= end_rad
                elif self.include_start:
                    return start_rad <= angle_rad < end_rad
                elif self.include_end:
                    return start_rad < angle_rad <= end_rad
                else:
                    return start_rad < angle_rad < end_rad
            else:
                if self.include_start and self.include_end:
                    return angle_rad >= start_rad or angle_rad <= end_rad
                elif self.include_start:
                    return angle_rad >= start_rad or angle_rad < end_rad
                elif self.include_end:
                    return angle_rad > start_rad or angle_rad <= end_rad
                else:
                    return angle_rad > start_rad or angle_rad < end_rad
                    
        elif isinstance(item, AngleRange):
            if self.include_start and self.include_end:
                if item.include_start:
                    if not (item.start in self):
                        return False
                else:
                    test_angle = Angle(item.start._radians + 1e-10, 'radians')
                    if not (test_angle in self):
                        return False
                
                if item.include_end:
                    if not (item.end in self):
                        return False
                else:
                    test_angle = Angle(item.end._radians - 1e-10, 'radians')
                    if not (test_angle in self):
                        return False
                
                return True

            if item.start == item.end and not self.include_start and not self.include_end:
                return item.start not in self

            start_in = item.start in self
            end_in = item.end in self
            
            if not start_in and not end_in:
                return False

            if self.start._radians <= self.end._radians and item.start._radians <= item.end._radians:
                if item.start._radians >= self.end._radians or item.end._radians <= self.start._radians:
                    return False

                if not self.include_start and item.start._radians == self.start._radians:
                    return False
                if not self.include_end and item.end._radians == self.end._radians:
                    return False
                
                return True

            return start_in or end_in
            
        return False

    def __add__(self, other):
        if isinstance(other, (int, float, Angle)):
            if isinstance(other, Angle):
                offset = other._radians
            else:
                offset = float(other)
            
            new_start = Angle(self.start._radians + offset, 'radians')
            new_end = Angle(self.end._radians + offset, 'radians')
            
            return AngleRange(new_start, new_end, self.include_start, self.include_end)
        
        elif isinstance(other, AngleRange):
            result_ranges = []

            additions = [
                (self.start, other.start),
                (self.start, other.end),
                (self.end, other.start),
                (self.end, other.end)
            ]
            
            for p1, p2 in additions:
                sum_angle = p1 + p2
                point_range = AngleRange(sum_angle, sum_angle, True, True)
                if point_range not in result_ranges:
                    result_ranges.append(point_range)
            
            return result_ranges
            
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float, Angle)):
            if isinstance(other, Angle):
                offset = other._radians
            else:
                offset = float(other)
            
            new_start = Angle(self.start._radians - offset, 'radians')
            new_end = Angle(self.end._radians - offset, 'radians')
            
            return AngleRange(new_start, new_end, self.include_start, self.include_end)
        
        elif isinstance(other, AngleRange):
            result_ranges = []

            subtractions = [
                (self.start, other.start),
                (self.start, other.end),
                (self.end, other.start),
                (self.end, other.end)
            ]
            
            for p1, p2 in subtractions:
                diff_angle = p1 - p2
                point_range = AngleRange(diff_angle, diff_angle, True, True)
                if point_range not in result_ranges:
                    result_ranges.append(point_range)
            
            return result_ranges
            
        return NotImplemented

def demo():
    print("Демонстрация класса Angle:")
    a1 = Angle(90, 'degrees')
    a2 = Angle(pi/2, 'radians')
    a3 = Angle(450, 'degrees')
    
    print(f"a1 = {a1}")
    print(f"a2 = {a2}")
    print(f"a3 = {a3}")
    print(f"a1 == a2: {a1 == a2}")
    print(f"a1 == a3: {a1 == a3}")
    print(f"float(a1): {float(a1)}")
    print(f"int(a1): {int(a1)}")
    print(f"a1 + a2 = {a1 + a2}")
    print(f"a1 - pi/2 = {a1 - pi/2}")
    print(f"a1 * 2 = {a1 * 2}")
    print(f"a1 / 2 = {a1 / 2}")
    
    print("\nДемонстрация класса AngleRange:")
    r1 = AngleRange(0, pi/2)  # [0, π/2]
    r2 = AngleRange(Angle(30, 'degrees'), Angle(60, 'degrees'))  # [30°, 60°]
    r3 = AngleRange(pi, 0, include_start=False, include_end=False)
    
    print(f"r1 = {r1}")
    print(f"r2 = {r2}")
    print(f"r3 = {r3}")
    print(f"Длина r1: {abs(r1)} рад")
    print(f"Длина r2: {abs(r2)} рад")
    
    # Проверка вхождения углов
    a4 = Angle(45, 'degrees')
    print(f"{a4} в r1: {a4 in r1}")
    print(f"{a4} в r2: {a4 in r2}")
    
    # Проверка вхождения диапазонов
    r4 = AngleRange(10, 50)
    print(f"{r4} в r1: {r4 in r1}")
    
    # Операции с диапазонами
    r5 = r1 + pi/4
    print(f"r1 + π/4 = {r5}")
    
    r6 = r1 - pi/4
    print(f"r1 - π/4 = {r6}")
    
    # Сложение двух диапазонов
    sum_ranges = r1 + r2
    print(f"r1 + r2 = {sum_ranges}")

if __name__ == "__main__":
    demo()