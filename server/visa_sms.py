from iso8583.specs import default as spec


spec['h']['data_enc'] = 'b'
spec['h']['max_len'] = 22

spec['t']['data_enc'] = 'b'
spec['t']['len_count'] = 'nibbles'
spec['t']['left_pad'] = '0'


spec['2']['data_enc'] = 'b'
spec['2']['len_count'] = 'nibbles'
spec['2']['left_pad'] = '0'
# @note: only for Variable length fields
spec['2']['len_enc'] = 'b'
# @note: for binary or bcd use len_type=1 as variable length type
spec['2']['len_type'] = 1

for x in range(3,17):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'

spec['17']['data_enc'] = 'b'

for x in range(18,28):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'

spec['28']['data_enc'] = 'cp500'

for x in range(32,37):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'
    spec[f"{x!r}"]['len_enc'] = 'b'
    spec[f"{x!r}"]['len_type'] = 1


spec['37']['data_enc'] = 'cp500'
spec['38']['data_enc'] = 'cp500'
spec['39']['data_enc'] = 'cp500'
spec['41']['data_enc'] = 'cp500'
spec['42']['data_enc'] = 'cp500'
spec['43']['data_enc'] = 'cp500'

for x in range(44, 49):
    spec[f"{x!r}"]['data_enc'] = 'cp500'
    # @note: only for Variable length fields
    spec[f"{x!r}"]['len_enc'] = 'b'
    # @note: for binary or bcd use len_type=1 as variable length type
    spec[f"{x!r}"]['len_type'] = 1

for x in range(49, 52):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'

spec['53']['data_enc'] = 'b'
spec['53']['len_count'] = 'nibbles'
spec['53']['left_pad'] = '0'

for x in range(54, 60):
    spec[f"{x!r}"]['data_enc'] = 'cp500'
    # @note: only for Variable length fields
    spec[f"{x!r}"]['len_enc'] = 'b'
    # @note: for binary or bcd use len_type=1 as variable length type
    spec[f"{x!r}"]['len_type'] = 1

for x in range(60,64):
    spec[f"{x!r}"]['data_enc'] = 'b'
    # @note: only for Variable length fields
    spec[f"{x!r}"]['len_enc'] = 'b'
    # @note: for binary or bcd use len_type=1 as variable length type
    spec[f"{x!r}"]['len_type'] = 1

for x in range(66, 91):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'

spec['91']['data_enc'] = 'cp500'
spec['92']['data_enc'] = 'cp500'
spec['94']['data_enc'] = 'cp500'
spec['95']['data_enc'] = 'cp500'
spec['97']['data_enc'] = 'cp500'
spec['98']['data_enc'] = 'cp500'

for x in range(99, 101):
    spec[f"{x!r}"]['data_enc'] = 'b'
    spec[f"{x!r}"]['len_count'] = 'nibbles'
    spec[f"{x!r}"]['left_pad'] = '0'
    spec[f"{x!r}"]['len_enc'] = 'b'
    spec[f"{x!r}"]['len_type'] = 1

for x in range(101, 105):
    spec[f"{x!r}"]['data_enc'] = 'b'
    # @note: only for Variable length fields
    spec[f"{x!r}"]['len_enc'] = 'b'
    # @note: for binary or bcd use len_type=1 as variable length type
    spec[f"{x!r}"]['len_type'] = 1

spec['104']['max_len'] = 255
