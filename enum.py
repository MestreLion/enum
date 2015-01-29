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

'''Basic replacement of enum module for Python < 3.4'''

__all__ = ['Enum']  # not necessary as Enum is the only non-__*__ name

import sys

class _meta(type):
    def _members(self):
        return [_ for _ in self.__dict__.items()
                if  not _[0].startswith("_")
                and not _[0] in ['name'] + getattr(self, '__non_members__', [])
                ]

    def __iter__(self):  # "self" for a metaclass refers to classes, not instances
        '''Yield members sorted by value, not declaration order'''
        for value in sorted([_[1] for _ in self._members()]):
            yield value

    def __len__(self):
        return len(self._members())


class _base(object):
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

# Python 3.1 - 3.3
elif sys.version_info[1] < 4:
    # Python 2 see Python 3 metaclass declaration as SyntaxError, hence exec()
    exec("class Enum(_base, metaclass=_meta):"
         "'''A basic implementation of Enums for Python 3 < 3.4'''")

# Python 3.4 onwards, wrap standard library
else:
    try:
        import enum
        Enum = enum.Enum
        del enum
    except ImportError:
        raise

del sys, _base, _meta


if __name__ == '__main__':
    # Usage and Examples

    class Color(Enum):
        '''Enum class example'''

        # Declaration order is irrelevant, sorting will always be by value
        # Values don't have to be numbers, but in Python 3 must be homogeneous
        BLACK    =  0
        WHITE    = 10  # This will sort last
        DEFAULT  = -1  # This will sort first
        RED      =  1
        GREEN    =  2
        BLUE     =  3
        NICE_ONE =  5

        @classmethod
        def name(cls, v):
            '''Optional custom name function'''
            if   v == cls.BLACK: return "is back!"
            elif v == cls.WHITE: return "Delight"

            # Uses default name as fallback for members not listed above
            else: return super(Color, cls).name(v)

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

    # Class type, inheritance, structure
    print (type(Color), "is Enum?", issubclass(Color, Enum))  # <class '__main__._meta'>, True
    print("MRO:", Color.mro())   # Color, Enum, _base, object
    print("class:", dir(Color))  # only members, 'name', and the default __*__

    # Module cleanness
    del Color, color
    print("module:", globals())  # only Enum and the default __*__
