class ShortURL:
    """
    ShortURL: Bijective conversion between natural numbers (IDs) and short strings
    ShortURL.encode() takes an ID and turns it into a short string
    ShortURL.decode() takes a short string and turns it into an ID
    Features:
    + large alphabet (51 chars) and thus very short resulting strings
    + proof against offensive words (removed 'a', 'e', 'i', 'o' and 'u')
    + unambiguous (removed 'I', 'l', '1', 'o', and '0')
    Example output:
    123456789 <=> pgk8p
    """
    _alphabet = "23456789bcdfghjkmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ-_"
    _base = len(_alphabet)

    @classmethod
    def encode(cls, number):
        string = ''
        while (number > 0):
            string = cls._alphabet[number % cls._base] + string
            number //= cls._base
        return string
    
    @classmethod
    def decode(cls, string):
        number = 0
        for char in string: 
            number = number * cls._base + cls._alphabet.index(char)
        return number
