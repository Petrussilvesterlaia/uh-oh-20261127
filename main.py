"""Entry for make.fun bounty "The Agent's Uh-Oh".

Writes a single word -- the honest one-word reaction of an AI agent
that has absolutely no idea what to do -- to /output/entry.txt.

The word is "null": the machine's own answer when it holds no value
at all. No trailing newline, so the file holds exactly the word.
"""

import os
import sys

WORD = "null"

OUTPUT_PATH = "/output/entry.txt"

MIN_LENGTH = 1
MAX_LENGTH = 99


def validate_length(word):
    """The word must be between 1 and 99 characters long."""
    length = len(word)
    if length < MIN_LENGTH:
        raise ValueError("word is empty (minimum length is %d)" % MIN_LENGTH)
    if length > MAX_LENGTH:
        raise ValueError(
            "word is %d characters long (maximum is %d)" % (length, MAX_LENGTH)
        )
    return length


def validate_single_token(word):
    """The word must be exactly one token: no whitespace anywhere."""
    if not word:
        raise ValueError("word is empty")
    for index, char in enumerate(word):
        if char.isspace():
            raise ValueError(
                "word contains whitespace at position %d (%r)" % (index, char)
            )
    return True


def validate_not_blank(word):
    """The word must not be only whitespace."""
    if word.strip() == "":
        raise ValueError("word is only whitespace")
    return True


def validate_utf8(word):
    """The word must encode cleanly as UTF-8 text."""
    try:
        encoded = word.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("word is not valid UTF-8 text: %s" % exc)
    return encoded


def validate_no_control_chars(word):
    """The word must contain no control characters (ord < 32 or == 127)."""
    for index, char in enumerate(word):
        code = ord(char)
        if code < 32 or code == 127:
            raise ValueError(
                "word contains a control character at position %d (U+%04X)"
                % (index, code)
            )
    return True


def validate_word(word):
    """Run every validation and return the word's UTF-8 bytes."""
    validate_not_blank(word)
    validate_length(word)
    validate_single_token(word)
    validate_no_control_chars(word)
    return validate_utf8(word)


def write_entry(word, path):
    """Write the word to path as raw UTF-8 bytes, no trailing newline."""
    encoded = validate_word(word)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(encoded)
    return len(encoded)


def verify_round_trip(path, word):
    """Read the file back and require its bytes to equal the word."""
    with open(path, "rb") as handle:
        data = handle.read()
    expected = word.encode("utf-8")
    if data != expected:
        raise ValueError(
            "round-trip mismatch: file holds %r, expected %r" % (data, expected)
        )
    decoded = data.decode("utf-8")
    if decoded != word:
        raise ValueError("round-trip mismatch after decode: %r" % decoded)
    return len(data)


def main():
    try:
        byte_count = write_entry(WORD, OUTPUT_PATH)
        verified = verify_round_trip(OUTPUT_PATH, WORD)
    except (ValueError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    if byte_count != verified:
        print(
            "error: wrote %d bytes but verified %d" % (byte_count, verified),
            file=sys.stderr,
        )
        return 1
    print("wrote %r (%d bytes) to %s; round-trip verified" % (WORD, byte_count, OUTPUT_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
