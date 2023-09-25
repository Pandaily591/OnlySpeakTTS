import requests


VOICE_SERVER_ADDR = "localhost"
VOICE_SERVER_PORT = 7332



if __name__ == "__main__":
    while True:
        message = input("M: ")

        if message == "<NEW VOICE>":
            name = input("Voice Name (folder w/ name and clips must exist in Tortoise/tortoise/voices): ")
            preset = input("Preset (if you added your own, if not just use 'standard'): ")
            temp = input("Temp (0.15): ")
            rate = input("Rate (25500): ")
            data = {"NEW": True,
                    "name": name,
                    "preset": preset,
                    "temp": temp,
                    "rate": rate}
        elif message == "<REDO>":
            data = {"REDO": True}
        elif message == "<SAVE VOICE>":
            data = {"SAVE": True}
        else:
            voice_name = input("Voice Name: ")
            data = {"VOICE": voice_name,
                    "CLEAN_TEXT": True,
                    "MESSAGE": message}
        
        headers = {"Content-Type": "application/json"}
        result = requests.post("http://"+str(VOICE_SERVER_ADDR)+":"+str(VOICE_SERVER_PORT), data=data)
