from Segment.Segment import Segment


if __name__ == "__main__":
    import os

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "README.md")
    segs = Segment()
    with open(filename, "rb") as src:
        segs.set_data(src.read(32768))
        print(segs)
        ment = Segment()
        ment.set_all_from_bytes(segs.get_all_as_bytes())
        print(ment)
