# IPScanner 🔬
A simple threaded IP-Scanner written in python3 that can monitor local IP's in your network.


#### Demo:
https://user-images.githubusercontent.com/63909127/152237702-cbaee6bd-7f45-42fe-9ce7-dd98a37b7fec.mp4

## Installation 💿
```bash
git clone https://github.com/Jonathan357611/ipscanner.git
cd ipscanner
pip3 install -r requirements.txt
python3 main.py <arguments>
```

## Usage ⚒️
#### Arguments
- -h: Displays help message
- -t: Set threads (default=255) (max.=255)
- -s: Set start of IP-range (default=192.168.178.1)
- -e: Set end of IP-range (default=192.168.178.255)
- -o: Set timeout in ms (default=500ms)

---

When the program has scanned every selected address,
press any key to see the results (IP, Hostname, Responsetime)

## Notes 📝
I'd be happy if you suggest, fix, add, etc. something as I am still learning :)
Any feedback is also very appreciated!

The Code was formated with [black](https://github.com/psf/black). Thanks for that software!

## TODO 📋

- Add multiple collumn support in the result screen.
- Scan ports

###### Anything else?
