pchars = "abcdefghijklmnopqrstuvwxyz,.?!'()[]{}┬─┬_"
fchars = "ɐqɔpǝɟƃɥıɾʞlɯuodbɹsʇnʌʍxʎz'˙¿¡,)(][}{┻━┻─"
# Flipping only works one way, pchars -> fchars
flipper = dict(zip(pchars, fchars))


def flip(s):
    charlist = [flipper.get(x, x) for x in s.lower()]
    charlist.reverse()
    return "".join(charlist)
