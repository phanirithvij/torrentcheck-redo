import sys, os, hashlib, io, bencode
from tqdm import tqdm


def pieces_generator(info):
    """Yield pieces from download file(s)."""
    piece_length = info["piece length"]
    if "files" in info:  # yield pieces from a multi-file torrent
        piece = b""
        for file_info in info["files"]:
            path = os.sep.join([info["name"]] + file_info["path"])
            print(path)
            sfile = open(path, "rb")
            while True:
                piece += sfile.read(piece_length - len(piece))
                if len(piece) != piece_length:
                    sfile.close()
                    break
                yield piece
                piece = b""
        if piece != b"":
            yield piece
    else:  # yield pieces from a single file torrent
        path = info["name"]
        print(path)
        sfile = open(path, "rb")
        while True:
            piece = sfile.read(piece_length)
            if not piece:
                sfile.close()
                return
            yield piece


def corruption_failure():
    """Display error message and exit"""
    print("download corrupted")


def main():
    # Open torrent file
    torrent_file = open(sys.argv[1], "rb")
    metainfo = bencode.decode(torrent_file.read())
    info = metainfo["info"]
    pieces = io.BytesIO(info["pieces"])
    # Iterate through pieces
    for piece in tqdm(pieces_generator(info)):
        # Compare piece hash with expected hash
        piece_hash = hashlib.sha1(piece).digest()
        readd = pieces.read(20)
        if piece_hash != readd:
            print(piece_hash, readd, len(readd), len(piece_hash))
            corruption_failure()
    # ensure we've read all pieces
    if pieces.read():
        corruption_failure()


if __name__ == "__main__":
    main()
