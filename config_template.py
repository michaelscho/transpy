# export
export_folder="/path/to/folder/"

resources_folder = "/path/to/folder/"

exist_url = "url/to/existdb/"

special_characters_dict = {'-ur':'\uF1C2',
        '-bus':'\uF1AC',
        'b mit Strich':'\u0180',
        'd mit Strich':'\u0111',
        'h mit Strich':'\u0127',
        'K mit Strich':'\uA740',
        'k mit Strich':'\uA741',
        'L mit hohem Strich':'\uA748',
        'l mit hohem Strich':'\uA749',
        'l mit mittlerem Strich':'\u019A',
        'Pre':'P\u0304',
        'pre':'p\u0304',
        'Per':'\uA750',
        'per':'\uA751',
        'Pro':'\uA752',
        'pro':'\uA753',
        'Nasalstrich':'\u0304',
        'Kürzungsstrich':'\u0305',
        'q mit Strich':'\uA757',
        'q mit Schlaufe':'\uA759',
        '-rum':'\ua75D',
        '-RUM':'\ua75C',
        '-us':'\u1DD2',
        '-a (hochgestellt)':'\u1DD3',
        '-i (hochgestellt)':'\u0365',
        'hochgestelltes -o':'\u0366',
        'hochgestelltes -u':'\u0367',
        'Antwort-Zeichen R':'\u211E',
        'Q mit Strich':'\uA756',
        'Q mit Schlaufe':'\uA758'}

def manual_expansion(word):
    rules_for_expansion = {'om̅': 'omn',
    '\uF1C2': 'ur',
    'P\u0304': 'Prae',
    'p\u0304': 'prae',
    '\uA750': 'Per',
    '\uA751': 'per',
    '\uA752': 'Pro',
    '\uA753': 'pro',
    '\u0304': 'm',
    '\ua75D': 'rum',
    '\ua75C': 'RUM',
    'q\uf1ac': 'que',
    'Q\u0366': 'Quo',
    'q\u0366': 'quo',
    'q\u1dd3': 'qua',
    'Q\u1dd3': 'Qua',
    'q\u0365': 'qui',
    'Q\u0365': 'Qui',
    'p\u0365': 'pri',
    'b\uf1ac': 'bus',
    '\u1DD2': 'us',
    'c\u0305': 'con',
    'C\u0305': 'Con',
    'm\u0305': 'men',
    't̅': 'ter',
    'r̅': 'runt'}
