#!/usr/bin/env python
# By Jonathan F.
import curses
import sys
import getopt
import netaddr
import threading
import time
import ping3
import socket

ping3.EXCEPTIONS = True


def PrintAndExit(text):
    curses.endwin()
    print(text)
    sys.exit(2)


class GetIpInfo(threading.Thread):
    def __init__(self, data):
        super(GetIpInfo, self).__init__()
        self.ips = data["ips"]
        self.stdsrc = data["stdsrc"]
        self.timeout = data["timeout"]
        self.results = {"total_scanned": 0, "online": 0, "online_ip_data": []}

    def run(self):
        for data in self.ips:  # First, draw all ip's in yellow
            ip = data[0]
            column = data[1]
            row = data[2]

            self.stdsrc.addstr(column, row, str(ip), curses.color_pair(2))

        for data in self.ips:  # Now scan every ip
            ip = data[0]
            column = data[1]
            row = data[2]
            self.temp_data_list = []

            try:
                response_time = ping3.ping(str(ip), timeout=self.timeout)
                self.stdsrc.addstr(column, row, str(ip), curses.color_pair(4))
                self.results["online"] += 1
                # Get more data about the current IP
                ## Get Hostname
                try:
                    hostname = socket.gethostbyaddr(str(ip))[0]
                except:
                    hostname = "<No hostname>"

                # Append gathered data
                self.temp_data_list.append(str(ip))
                self.temp_data_list.append(hostname)
                self.temp_data_list.append(response_time)

            except:
                self.stdsrc.addstr(column, row, str(ip), curses.color_pair(3))

            self.results["online_ip_data"].append(self.temp_data_list)
            self.results["total_scanned"] += 1


def main(stdsrc):
    height, width = stdsrc.getmaxyx()  # Get terminal dimensions

    # Get passed arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":h:t:s:e:o:")
    except getopt.GetoptError:  # If "-h" is passed, it raises this error.
        PrintAndExit(
            "-h : This help message\n-t : Specify threads (default=255)\n-s : Start of IP-range (default=192.168.1.1)\n-e: End of IP-range (default=192.168.1.255)\n-o : timeout in milliseconds"
        )

    # Default values
    range_start = "192.168.1.1"
    range_end = "192.168.1.255"
    threads = 255
    timeout = 5

    # Replace default values when requested with "opt"
    for opt, arg in opts:
        if opt == "-h":
            PrintAndExit(
                "-h : This help message\n-t : Specify threads (default=255)\n-s : Start of IP-range (default=1)\n-e: End of IP-range (default=255)"
            )

        elif opt == "-t":
            if arg.isdigit():
                if int(arg) <= 255 and int(arg) >= 1:
                    threads = int(arg)
                else:
                    PrintAndExit(f"{opt} has to be <255 and >1!")
            else:
                PrintAndExit(f"{opt} has to be numeric!")

        if opt == "-s":
            range_start = arg
        elif opt == "-e":
            range_end = arg
        elif opt == "-o":
            timeout = float(arg) / 1000

    try:
        all_ips = list(netaddr.iter_iprange(range_start, range_end))
    except Exception as e:
        PrintAndExit(f"{e}\nPlease enter valid start and end IP's.")
    if all_ips == []:
        PrintAndExit("The range-start has to be smaller than the range-end")

    if threads >= len(all_ips):
        threads = len(all_ips)

    # Init color pairs
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    CYAN_BLACK = curses.color_pair(1)
    YELLOW_BLACK = curses.color_pair(2)
    RED_BLACK = curses.color_pair(3)
    GREEN_BLACK = curses.color_pair(4)

    # Display initial placeholder text which will be updated later
    curses.curs_set(0)  # Disable blinking curser
    stdsrc.clear()
    stdsrc.addstr(
        1, 2, f"Threads: {threads}         Timeout: {timeout*1000}ms", CYAN_BLACK
    )
    stdsrc.addstr(2, 2, f"Scanning... [0/{len(all_ips)}]", YELLOW_BLACK)
    stdsrc.addstr(3, 2, "_" * (width - 2), CYAN_BLACK)
    stdsrc.refresh()

    # split all_ips in a total of len(threads) lists
    chunked_list = []
    chunk_size = int(threads)
    sub_list = []
    n = 0
    for ip in all_ips:
        n += 1
        sub_list.append(ip)
        if n == round(len(all_ips) / int(threads)):
            chunked_list.append(sub_list)
            sub_list = []
            n = 0
    if chunked_list != []:  # Append the overflowen data to the last thread's list
        chunked_list.append(sub_list)

    # Start threads:
    i = 0
    curr_row = 2
    for ips in chunked_list:
        data = {
            "ips": list(),
            "stdsrc": stdsrc,
            "timeout": timeout,
        }
        for ip in ips:
            if i + 6 > height - 1:
                i = 0
                curr_row += 25
            data["ips"].append(
                [ip, i + 5, curr_row]
            )  # Append IP's to the "data" object, which will be passed to a thread.
            i += 1

        # Start thread
        thread = GetIpInfo(data)
        all_threads.append(thread)
        thread.start()

    # While there are threads active, update the display
    while True:
        ips_scanned = 0
        for thread in all_threads:
            ips_scanned += thread.results["total_scanned"]

        if ips_scanned != len(all_ips):
            stdsrc.addstr(
                2, 2, f"Scanning... [{ips_scanned}/{len(all_ips)}]", YELLOW_BLACK
            )
        else:
            stdsrc.addstr(
                2, 2, f"Scanned! [{ips_scanned}/{len(all_ips)}]     ", GREEN_BLACK
            )
            break

        stdsrc.refresh()
        time.sleep(0.1)

    stdsrc.addstr(height - 1, 2, "Press any key to see the results.", CYAN_BLACK)
    stdsrc.refresh()
    stdsrc.getch()
    stdsrc.clear()

    total_online = 0
    i = 5
    last_ip = ".0"
    for thread in all_threads:
        total_online += thread.results["online"]

        data = thread.results["online_ip_data"]
        for entry in data:
            if entry != []:
                ip = str(entry[0])
                hostname = entry[1]
                response_time = entry[2]

                if int(last_ip.split(".")[-1]) + 1 != int(str(ip).split(".")[-1]):
                    stdsrc.addstr(i, 2, "...")
                    i += 1

                stdsrc.addstr(
                    i,
                    2,
                    f"{ip} ({round(response_time, 4)}ms){' '*(27-len(ip + ' (' + str(round(response_time, 4)) + 'ms)'))}-  {hostname}",
                    GREEN_BLACK,
                )

                last_ip = str(ip)
                i += 1

    ip_percentage = 0
    if total_online != 0:
        ip_percentage = round(total_online / len(all_ips) * 100, 3)

    stdsrc.addstr(2, 2, f"All done!", YELLOW_BLACK)
    stdsrc.addstr(
        3,
        2,
        f"Scanned {len(all_ips)} IP's with {threads} threads, {total_online} ({ip_percentage}%) of them where online!",
        CYAN_BLACK,
    )
    stdsrc.addstr(4, 2, "_" * (width - 2), CYAN_BLACK)

    stdsrc.getch()


if __name__ == "__main__":
    all_threads = []
    curses.wrapper(main)
