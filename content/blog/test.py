spam = 5


if isinstance(spam, float) or isinstance(spam, int):
    print("Hello")


if type(spam) == str or type(spam) == int:
    print("spam")

if type(spam) not in (str, int):
    print("test")
