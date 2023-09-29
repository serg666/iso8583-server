def build_response_mti(mti):
    """Build response MTI (message type identifier)
    """

    return mti[:2] + str(int(mti[2]) + 1) + mti[3]


def repr_call(name_, *args, **kwargs):
    return ''.join([
        name_,
        '(',
        ', '.join([repr(a) for a in args]),
        ', '.join(['%s=%r' % i for i in kwargs.items()]),
        ')'
    ])


class MaskedString(str):
    '''
    >>> ms =  MaskedString('foobar')
    >>> ms
    MaskedString('******')
    >>> str(ms)
    "MaskedString('******')"
    >>> ms =  MaskedString('foobar', show_last=4)
    >>> str(ms)
    "MaskedString('**obar')"
    >>> ms == 'foobar'
    True
    '''

    placeholder = '*'

    def __new__(cls, arg, placeholder=None, show_last=None, *args, **kwargs):
        return super(MaskedString, cls).__new__(cls, arg, *args, **kwargs)

    def __init__(self, arg, placeholder=None, show_last=None):
        super(MaskedString, self).__init__()
        self.placeholder = placeholder or self.placeholder
        self.show_last = show_last or 0

    @property
    def masked(self):
        l = len(self) - self.show_last
        last = ''
        if self.show_last > 0:
            last = self[-self.show_last:]
        return (self.placeholder * l) + last

    def __str__(self):
        return repr_call(type(self).__name__, self.masked)

    __repr__ = __str__


def mask_ddk(decoded):
    decoded_copy = decoded.copy()
    if '2' in decoded_copy:
        decoded_copy['2'] = MaskedString(decoded_copy['2'], show_last=4)
    return decoded_copy
