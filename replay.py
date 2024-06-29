import requests, json, os, zipfile, shutil, lzma
from maniera.calculator import Maniera


class Replay:
    def __init__(self, file):
        # .osr data types in bytes
        self.__BYTE = 1
        self.__SHORT = 2
        self.__INTEGER = 4
        self.__LONG = 8

        try:
            # Read replay data
            with open(file, "rb") as file:
                self.mode = self.__read(file, self.__BYTE)
                self.version = self.__read(file, self.__INTEGER)

                self.beatmap_md5 = self.__read_string(file)
                self.name = self.__read_string(file)
                self.replay_md5 = self.__read_string(file)

                self.n_300 = self.__read(file, self.__SHORT)
                self.n_100 = self.__read(file, self.__SHORT)
                self.n_50 = self.__read(file, self.__SHORT)
                self.n_geki = self.__read(file, self.__SHORT)
                self.n_katu = self.__read(file, self.__SHORT)
                self.n_miss = self.__read(file, self.__SHORT)

                self.score = self.__read(file, self.__INTEGER)
                self.combo = self.__read(file, self.__SHORT)
                self.perfect_combo = bool(self.__read(file, self.__BYTE))
                self.mods = self.__read(file, self.__INTEGER)

                self.graph = self.__read_string(file)

                self.timestamp = self.__read(file, self.__LONG)
                self.replay_data = lzma.decompress(self.__read_byte_array(file))
                self.online_score_id = self.__read(file, self.__LONG)

        except:
            raise Exception("Error: invalid file path")

        # Beatmap data
        try:
            self.__api_key = ""  # <-- API key goes here
            self.__url = requests.get(
                f"https://osu.ppy.sh/api/get_beatmaps?k={self.__api_key}&h={self.beatmap_md5}"
            )
            self.beatmap = json.loads(self.__url.text)[0]
        except:
            raise Exception("APIError: beatmap not found")

        # Maniera
        if self.mode == 3:
            self.__maniera = Maniera(self.__get_beatmap_path(), self.mods, self.score)
            self.__maniera.calculate()
            self.pp = self.__maniera.pp
            self.sr = self.__maniera.sr

            # Cleanup downloaded beatmap
            if os.path.exists("beatmap"):
                shutil.rmtree("beatmap")
        else:
            raise Exception("Error: invalid gamemode")

    def __read(self, file, type):
        return int.from_bytes(file.read(type), "little")  # All data types are little

    # Decode variable length integer
    def __decode_uleb128(self, file):
        result = 0
        shift = 0

        while True:
            byte = self.__read(file, self.__BYTE)
            result |= (byte & ~128) << shift  # Low-order 7 bits of byte << shift
            if byte & 128 == 0:  # High-order bit of byte == 0
                return result
            shift += 7

    # Read variable length string
    def __read_string(self, file):
        if file.read(self.__BYTE) == b"\x0b":
            length = self.__decode_uleb128(file)  # Decode length
            return file.read(length).decode("utf-8")

    # Read variable length byte array
    def __read_byte_array(self, file):
        length = self.__read(file, self.__INTEGER)
        byte_array = bytearray()
        for _ in range(length):
            byte = file.read(self.__BYTE)
            byte_array.extend(byte)
        return byte_array

    def __get_beatmapset_path(self):
        beatmapset_id = self.beatmap["beatmapset_id"]
        beatmapset_path = "beatmap"

        # Download beatmapset if not found in songs folder
        try:
            request = requests.get("https://catboy.best/d/" + beatmapset_id)
            with open("beatmap.osz", "wb") as file:
                file.write(request.content)
        except:
            raise Exception("APIError: download failed, beatmap not found")

        # Extract content into temp
        with zipfile.ZipFile("beatmap.osz") as file:
            file.extractall(beatmapset_path)

        os.remove("beatmap.osz")

        return beatmapset_path

    def __get_beatmap_path(self):
        beatmap_id = self.beatmap["beatmap_id"]
        beatmapset_path = self.__get_beatmapset_path()

        # For every file in beatmapset
        for file in os.listdir(beatmapset_path):
            # If .osu file
            if file.endswith(".osu"):
                with open(os.path.join(beatmapset_path, file)) as file:
                    # Find beatmap ID in osu file
                    for line in file.readlines():
                        # If beatmap id matches replay, return
                        if (
                            line.startswith("BeatmapID")
                            and line.split(":")[1].strip() == beatmap_id
                        ):
                            return file.name

    def calculate_accuracy(self):
        numerator = (
            (self.n_300 + self.n_geki) * 300
            + self.n_katu * 200
            + self.n_100 * 100
            + self.n_50 * 50
        )
        denominator = (
            self.n_300
            + self.n_geki
            + self.n_katu
            + self.n_100
            + self.n_50
            + self.n_miss
        ) * 300
        return numerator / denominator * 100

    def calculate_ma(self):
        return self.n_geki / self.n_300

    def get_mod_list(self):
        # Mods in order of bit position
        mods = [
            "NF",
            "EZ",
            "TD",
            "HD",
            "HR",
            "SD",
            "DT",
            "RX",
            "HT",
            "NC",
            "FL",
            "AO",
            "SO",
            "AP",
            "PF",
            "K4",
            "K5",
            "K6",
            "K7",
            "K8",
            "FI",
            "RD",
            "CN",
            "TP",
            "K9",
            "CO",
            "K1",
            "K3",
            "K2",
            "V2",
            "MR",
        ]

        mod_list = []
        bits = self.mods  # Copy mods into bits

        for _ in range(bits.bit_count()):
            position = bits.bit_length() - 1  # Position of next set bit
            mod_list.insert(0, mods[position])  # Add to front of modList
            bits = bits ^ 1 << position  # Unset bit

        return mod_list

    def decode_replay_data(self):
        events = self.replay_data.split(b",")  # Split replay data into events
        events = [event.split(b"|") for event in events]  # Split events into parts

        # Extract time and keys from events
        for i, e in enumerate(events):
            if len(e) == 4:
                time = int(e[0])
                key = int(e[1])
                events[i] = [time, key]

        return events
