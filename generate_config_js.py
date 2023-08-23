import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_mode", type=str, help="", default="online")
    args = parser.parse_args()

    mode_to_port = {
        "online": 12856,
        "debug": 12899
    }
    with open("pages/config1.js", "w") as fout:
        fout.write("var config = \{ apiUrl: \"http://192.168.12.225:{}/api/v0/tag_rank/\"\}".format(mode_to_port[args.start_mode]))
    with open("pages/config.js", "w") as fout:
        fout.write("var config = \{ apiUrl: \"http://192.168.12.225:{}/api/v0/tag_rank/\"\}".format(mode_to_port[args.start_mode]))


if __name__ == "__main__":
    main()
