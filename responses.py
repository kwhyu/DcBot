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
    elif '!bye' in lowered:
        return 'See you!'
    elif '!roll dice' in lowered:
        return f'You rolled: {randint(1, 6)}'
    else:
        return choice(['',
                       '',
                       ''])
