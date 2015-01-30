# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

'''Basic implementation of enum module for Python 2 and 3'''

__all__ = ['Enum']  # not necessary as Enum is the only non-__*__ name

import sys

class _meta(type):
    def __iter__(self):  # "self" for a metaclass refers to classes, not instances
        '''Yield members sorted by value, not declaration order'''
        for value in sorted(self.members().values()):
            yield value

    def __len__(self):
        return len(self.members())


class _base(object):
    @staticmethod
    def _callable(obj):
        '''Helper wrapper for callable() that works on Python 3.0 and 3.1'''
        try:
            return callable(obj)
        except NameError:
            # Python 3.0 and 3.1 has no callable()
            # which is a tiny safer than hasattr approach
            return hasattr(obj, "__call__")

    @classmethod
    def members(cls):
        return {k: v for k, v in cls.__dict__.items()
                if  not k.startswith("_")
                and not cls._callable(getattr(cls, k))}

    @classmethod
    def name(cls, value):
        '''
        Fallback for getting a member "name"
        Return a titled string with underscores replaced by spaces
            AnEnum.name(AnEnum.AN_ORDINARY_MEMBER) => "An Ordinary Member"
        Enums can customize member names by overriding this method
        '''
        # value as string, if it matches an enum attribute.
        # Allows short usage as Enum.name("VALUE") besides Enum.name(Enum.VALUE)
        if hasattr(cls, str(value)):
            return cls.name(getattr(cls, value, None))

        # value not handled in subclass name()
        for k, v in cls.__dict__.items():
            if v == value:
                return k.replace('_', ' ').title()

        # value not found
        raise KeyError("Value '%s' not found in enum '%s'" %
                       (value, cls.__name__))


# Python 2
if sys.version_info[0] < 3:
    class Enum(_base):
        '''A basic implementation of Enums for Python 2'''
        __metaclass__ = _meta

# Python 3
else:
    # Python 2 see Python 3 metaclass declaration as SyntaxError, hence exec()
    exec("class Enum(_base, metaclass=_meta):"
         "'''A basic implementation of Enums for Python 3'''")

del sys, _base, _meta


if __name__ == '__main__':
    # Usage and Examples

    class Color(Enum):
        '''Enum class example'''

        # Declaration order is irrelevant, sorting will always be by value
        # Values can be any non-callable, and in Python 3 must be comparable
        # Bottom line: don't make an Enum of functions,
        # and don't mix numbers with strings
        BLACK    =  0
        WHITE    = 10  # This will sort last
        DEFAULT  = -1  # This will sort first
        RED      =  1
        GREEN    =  2
        BLUE     =  3
        NICE_ONE =  4

        # Methods are not considered members
        # That's why member values cannot be callables

        @classmethod
        def name(cls, v):
            '''Optional custom name function'''
            if v == cls.BLACK: return "is back!"
            if v == cls.WHITE: return "Delight"

            # Uses default name as fallback for members not listed above
            return super(Color, cls).name(v)

        @classmethod
        def counterpart(cls, v):
            '''Custom method example'''
            if v in [cls.DEFAULT,
                     cls.NICE_ONE]: return v
            if v ==  cls.BLACK:     return cls.WHITE
            if v ==  cls.WHITE:     return cls.BLACK
            if v ==  cls.BLUE:      return cls.RED

            return v + 1

    # Value and types
    print(Color.RED, type(Color.RED))  # 1, <type 'int'>

    # Testing values
    print("Red is the new Black?",
          Color.BLACK == 1,  # False
          Color.BLACK == 0)  # True

    # Names
    print(Color.name(1))           # "Red"
    print(Color.name("GREEN"))     # "Green"
    print(Color.name(Color.BLUE))  # "Blue"

    # Auto-name formatting
    print(Color.name(Color.NICE_ONE))  # "Nice One"

    # Custom names
    print("Black", Color.name(Color.BLACK),  # "is back!"
          "White", Color.name(Color.WHITE))  # "Delight"

    # Membership
    print("is green a color?", Color.GREEN in Color)  # True

    # Iterating - automatically sorted by value
    for color in Color:
        print(color, Color.name(color))

    # Member count
    print("colors in a rainbow:", len(Color))  # 7

    # Using members() directly
    print("members:", Color.members())

    # Custom methods
    for color in Color:
        print(Color.name(color), "<=>", Color.name(Color.counterpart(color)))

    # Class type, inheritance, structure
    print (type(Color), "is Enum?", issubclass(Color, Enum))  # <class '__main__._meta'>, True
    print("MRO:", Color.mro())   # Color, Enum, _base, object
    print("class:", dir(Color))

    # Module cleanness
    del Color, color
    print("module:", globals())  # only Enum and the default __*__
