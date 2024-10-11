from random import choice, randint
# from responses import get_response



def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'apa tod'
    elif 'halo' in lowered:
        return 'oi oi oi oi'
    elif 'hello' in lowered:
        return '???'
    elif 'hbd' in lowered:
        return 'HBD OI OI OI OI'
    elif 'p adu' in lowered:
        return 'HUH !?'
    else:
        return choice(['',
                       '',
                       ''])
