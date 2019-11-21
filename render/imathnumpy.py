import numpy as np
import Imath
from ctypes import (
    c_bool, c_byte, c_ubyte, c_short, c_ushort,
    c_int, c_uint, c_float, c_double
) 

# ImathArrayType: (numpyDType, ctype, dim, dataShape)
_CONVERT_DICT = {
    # vertices
    Imath.V2fArray: (c_float,  1, (2,)),
    Imath.V2dArray: (c_double, 1, (2,)),
    Imath.V2sArray: (c_short,  1, (2,)),
    Imath.V2iArray: (c_int,    1, (2,)),
    Imath.V3fArray: (c_float,  1, (3,)),
    Imath.V3dArray: (c_double, 1, (3,)),
    Imath.V3sArray: (c_short,  1, (3,)),
    Imath.V3iArray: (c_int,    1, (3,)),
    Imath.V4fArray: (c_float,  1, (4,)),
    Imath.V4dArray: (c_double, 1, (4,)),
    Imath.V4sArray: (c_short,  1, (4,)),
    Imath.V4iArray: (c_int,    1, (4,)),

    # boxes
    Imath.Box2fArray: (c_float,  1, (2, 2)),
    Imath.Box2dArray: (c_double, 1, (2, 2)),
    Imath.Box2sArray: (c_short,  1, (2, 2)),
    Imath.Box2iArray: (c_int,    1, (2, 2)),
    Imath.Box3fArray: (c_float,  1, (2, 3)),
    Imath.Box3dArray: (c_double, 1, (2, 3)),
    Imath.Box3sArray: (c_short,  1, (2, 3)),
    Imath.Box3iArray: (c_int,    1, (2, 3)),

    # colors
    Imath.C3cArray: (c_byte,   1, (3,)),
    Imath.C3fArray: (c_float,  1, (3,)),
    Imath.C4cArray: (c_byte,   1, (4,)),
    Imath.C4fArray: (c_float,  1, (4,)),

    # images
    Imath.Color4cArray2D: (c_byte,   2, (4,)),
    Imath.Color4fArray2D: (c_float,  2, (4,)),

    # matrices
    Imath.M33fArray: (c_float,  1, (3, 3)),
    Imath.M33dArray: (c_double, 1, (3, 3)),
    Imath.M44fArray: (c_float,  1, (4, 4)),
    Imath.M44dArray: (c_double, 1, (4, 4)),

    # rotations
    Imath.QuatfArray:  (c_float,  1, (4,)),
    Imath.QuatdArray:  (c_double, 1, (4,)),
    Imath.EulerfArray: (c_float,  1, (3,)),
    Imath.EulerdArray: (c_double, 1, (3,)),

    # raw numerical
    Imath.FloatArray:         (c_float,  1, ()),
    Imath.FloatArray2D:       (c_float,  2, ()),
    Imath.DoubleArray:        (c_double, 1, ()),
    Imath.DoubleArray2D:      (c_double, 2, ()),
    Imath.IntArray:           (c_int,    1, ()),
    Imath.IntArray2D:         (c_int,    2, ()),
    Imath.BoolArray:          (c_bool,   1, ()),
    Imath.ShortArray:         (c_short,  1, ()),
    Imath.SignedCharArray:    (c_byte,   1, ()),
    Imath.UnsignedCharArray:  (c_ubyte,  1, ()),
    Imath.UnsignedIntArray:   (c_uint,   1, ()),
    Imath.UnsignedShortArray: (c_ushort, 1, ()),

    # string pointers.
    # Not really sure what to do with these off the top of my head
    #Imath.StringArray:  (c_char_p,  1, ())
    #Imath.WstringArray: (c_wchar_p, 1, ())

    # No idea what this is
    #Imath.VIntArray
}

def arrayToNumpy(ImathArray):
    """ Wrap the given Imath array as a numpy array
    The returned numpy array will share memory with the Imath array.
    """
    # Get the conversion data
    tpe = type(ImathArray)
    if tpe not in _CONVERT_DICT:
        raise TypeError("Unrecognized type: {0}".format(tpe))
    ctype, dim, dataShape = _CONVERT_DICT[tpe]

    # Build the shape of the numpy array
    if dim == 1:
        shape = (len(ImathArray),) + dataShape
    elif dim == 2:
        shape = ImathArray.size() + dataShape

    # Create the ctypes data pointer
    cdata = ctype
    for component in reversed(shape):
        # this multiplication effectively prepends 
        # a new dimension to the ctype data shape
        # hence the reversed loop
        cdata = cdata * component

    # This ctypes array will get garbage collected, but that's OK
    # because we have the numpy array already pointing at the
    # internal Imath array data under the hood
    cta = cdata.from_address(ImathArray.address())

    # Return the numpy array
    return np.ctypeslib.as_array(cta)


