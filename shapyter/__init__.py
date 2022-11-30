import random
import itertools
import math


class Shape:
    def __init__(self, form, fill="white", dur=None):
        self._form = form
        self._stroke = "black"
        self._fill = fill
        self._size = 16
        self._line_width = 1.5
        self._dur = 1 if dur is None else dur
    
    def __eq__(self, other):
        return (self._form, self._fill) == (other._form, other._fill)
    
    def __hash__(self):
        return hash((self._form, self._fill))
    
    @property
    def svg(self):
        raise NotImplementedError()

    def _repr_html_(self):
        return self.svg

    
class Circle(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__("circle", *args, **kwargs)

    @property
    def svg(self):
        size = self._size
        lw = self._line_width
        dur = self._dur
        return f"""
            <svg width="{size}" height="{size}">
                <circle cx="{size / 2}" cy="{size / 2}" r="{size // 2 - lw}"
                    stroke="{self._stroke}" stroke-width="{lw}" fill="{self._fill}">
                    
                    <animate
                       attributeName="stroke-width" values="{lw * 2};0;{lw * 2}"
                       dur="{dur}s" repeatCount="indefinite" calcMode="discrete" />
                    
                </circle>
            </svg>
            """

    def __repr__(self):
        return f'Circle("{self._fill}")'

        
class Square(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__("square", *args, **kwargs)
        
    @property
    def svg(self):
        size = self._size
        lw = self._line_width
        dur = self._dur
        return f"""
            <svg width="{size}" height="{size}">
                <rect x="{lw}" y="{lw}"
                    width="{size - lw * 2}" height="{size - lw * 2}"
                    stroke="{self._stroke}" stroke-width="{lw}"
                    fill="{self._fill}">

                    <animate
                       attributeName="stroke-width" values="{lw * 2};0;{lw * 2}"
                       dur="{dur}s" repeatCount="indefinite" calcMode="discrete" />

                </rect>
            </svg>
            """

    def __repr__(self):
        return f'Square("{self._fill}")'
    
    
class Triangle(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__("triangle", *args, **kwargs)

    @property
    def svg(self):
        size = self._size
        lw = self._line_width
        dur = self._dur
        return f"""
            <svg width="{size}" height="{size}">
                <polygon points="
                    {lw},{size - lw}
                    {size - lw},{size - lw}
                    {size // 2},{lw}"
                    stroke="{self._stroke}" stroke-width="{lw}"
                    fill="{self._fill}" >

                    <animate
                       attributeName="stroke-width" values="{lw * 2};0;{lw * 2}"
                       dur="{dur}s" repeatCount="indefinite" calcMode="discrete" />

                </polygon>
            </svg>
            """

    def __repr__(self):
        return f'Triangle("{self._fill}")'
        

class Set(Shape):
    def __init__(self, value, bits):
        super().__init__(("matrix", value))
        self._value = value
        self._cell_size = 16
        self._bits = bits
        if value < 0 or value >= (1 << bits):
            raise ValueError(bits)
        self._bits_sqrt = int(math.ceil(math.sqrt(bits)))
        self._size = self._bits_sqrt * self._cell_size
        self._stroke = "black"
                
    def jaccard(self, other):
        x = self._value & other._value
        return bin(x).count("1") / self._bits
        
    @property
    def svg(self):
        size = self._size
        lw = self._line_width
        #dur = self._dur
        n = self._bits_sqrt
        rects = []
        margin = 1.5
        
        for x in range(n):
            for y in range(n):        
                i = x + y * n
                fill = "black" if ((self._value >> i) & 1) != 0 else "white"
        
                rects.append(
                    f"""<rect
                        x="{self._cell_size * x + margin}"
                        y="{self._cell_size * y + margin}"
                        width="{self._cell_size - 2 * margin}"
                        height="{self._cell_size - 2 * margin}"
                        stroke="{self._stroke}" stroke-width="{lw}"
                        fill="{fill}" />""")
        
        return f"""
            <svg width="{size}" height="{size}">
                {''.join(rects)}
            </svg>
            """
    
        
class List(list):
    def _repr_html_(self):
        return "[" + ", ".join([
            f"<span>{x._repr_html_()}</span>" for x in self]) + "]"

    
class Shapifier:
    forms = [Triangle, Square, Circle]
    colors = ["#86AED1", "#F8C3B6", "#F8EBBF", "#AEBC6E", "#679A7D"]
    dur = [1.25, 2.2, 2.8]
    
    def __init__(self, seed=None):
        self._shapes = dict()
        self._pool = list(itertools.product(
            Shapifier.forms, Shapifier.colors, Shapifier.dur))
        r = random.Random(seed)
        r.shuffle(self._pool)
    
    def _random_shape(self):
        if not self._pool:
            raise RuntimeError("no shapes left")
        form, color, dur = self._pool.pop()
        return form(color, dur=dur)
        
    def __call__(self, seq):
        shapes_seq = []
        for x in seq:
            shape = self._shapes.get(x)
            if shape is None:
                shape = self._random_shape()
                self._shapes[x] = shape
            shapes_seq.append(shape)
        
        return List(shapes_seq)
