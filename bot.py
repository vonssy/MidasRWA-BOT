from curl_cffi import requests
from urllib.parse import parse_qs, unquote
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import time, json, os, random, pytz

wib = pytz.timezone('Asia/Jakarta')

class MidasRWA:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'api-tg-app.midas.app',
            'Origin': 'https://prod-tg-app.midas.app',
            'Pragma': 'no-cache',
            'Referer': 'https://prod-tg-app.midas.app/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random
        }
        self.source = 'ref_b6243c03-25ae-43f0-9667-5defd6c43b9b'
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Midas RWA - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            response = requests.get(url=url, timeout=10)
            response.raise_for_status()
            content = response.text
            with open('proxy.txt', 'w') as f:
                        f.write(content)

            self.proxies = content.splitlines()
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                return
            
            self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            time.sleep(3)
        except requests.RequestsError as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            time.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def load_data(self, query: str):
        query_params = parse_qs(query)
        query = query_params.get('user', [None])[0]

        if query:
            user_data_json = unquote(query)
            user_data = json.loads(user_data_json)
            first_name = user_data.get("first_name", "Unknown")
            return first_name
        else:
            raise ValueError("User data not found in query.")
    
    def user_register(self, query: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/auth/register'
        data = json.dumps({'initData':query, 'source':self.source})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, data=data, proxy=proxy, timeout=10, impersonate="safari15_5")    
                response.raise_for_status()
                return response.text
            except requests.RequestsError as e:
                self.log(f"Error: {str(e)}")
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def user_data(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/user'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def user_visited(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/user/visited'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.patch(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def daily_checkin(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/streak'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def claim_checkin(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/streak'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def refferal(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/referral/status'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def claim_refferal(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/referral/claim'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def game_play(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/game/play'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def tasks(self, token: str, proxy: str, retries=5):
        url = 'https://api-tg-app.midas.app/api/tasks/available'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def start_tasks(self, token: str, task_id: str, proxy: str, retries=5):
        url = f'https://api-tg-app.midas.app/api/tasks/start/{task_id}'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                if response.status_code == 400:
                    return None
                
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def claim_tasks(self, token: str, task_id: str, proxy: str, retries=5):
        url = f'https://api-tg-app.midas.app/api/tasks/claim/{task_id}'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=10, impersonate="safari15_5")
                if response.status_code == 400:
                    return None
                
                response.raise_for_status()
                return response.json()
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto" if choose == 1 else 
                        "With Manual" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    time.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
        
    def process_query(self, query: str, use_proxy: bool):
        first_name = self.load_data(query)
        
        proxy = None
        if use_proxy:
            proxy = self.get_next_proxy()

        token = None
        while token is None:
            token = self.user_register(query, proxy)
            if not token:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {first_name} {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}GET Token Failed{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} With Proxy {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )

                if not use_proxy:
                    return

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Retrying With Next Proxy... {Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                proxy = self.get_next_proxy()
                continue
        
            user = self.user_data(token, proxy)
            if not user:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {first_name} {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Data Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
                return

            first_visit = user['isFirstVisit']
            if first_visit:
                user = self.user_visited(token, proxy)
                if not user:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {first_name} {Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT}Data Is None{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    return

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {user['firstName']} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {user['points']} GM {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}] [ Tap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {user['tickets']} Left {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
            )
            time.sleep(5)

            checkin = self.daily_checkin(token, proxy)
            if checkin:
                claimable = checkin['claimable']
                if claimable:
                    claim = self.claim_checkin(token, proxy)
                    if claim and not claim['claimable']:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {claim['streakDaysCount']} {Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin['nextRewards']['points']} GM {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin['nextRewards']['tickets']} Tap {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {claim['streakDaysCount']} {Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} Day {checkin['streakDaysCount']} {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Is Already Claimed{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
            time.sleep(5)

            refferal = self.refferal(token, proxy)
            if refferal:
                can_claim = refferal['canClaim']
                if can_claim:
                    claim = self.claim_refferal(token, proxy)
                    if claim and claim['message'] == 'Rewards claimed successfully':
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {claim['totalPoints']} GM {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {claim['totalTickets']} Tap {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Rewards to Claim {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
            time.sleep(5)

            user = self.user_data(token, proxy)
            if user:
                ticket = user['tickets']
                if ticket > 0:
                    while ticket > 0:
                        tap_tap = self.game_play(token, proxy)
                        if tap_tap:
                            ticket -= 1
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Tap Tap{Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT} Is Success {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {tap_tap['points']} GM {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}] [ Chances{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {ticket} Left {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Tap Tap{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Isn't Success {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            break

                        time.sleep(3)

                    if ticket == 0:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Tap Tap{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Tap Tap{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Chance Left {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {first_name} {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}GET Tickets Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
            time.sleep(5)

            tasks = self.tasks(token, proxy)
            if tasks:
                completed = False
                for task in tasks:
                    task_id = task['id']
                    status = task['state']

                    if task and status == 'WAITING':
                        start = self.start_tasks(token, task_id, proxy)
                        if start and start['state'] == 'CLAIMABLE':
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Is Started{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                            )

                            delay = random.randint(15, 20)
                            for remaining in range(delay, 0, -1):
                                print(
                                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}Seconds to Claim Reward{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}  ",
                                    end="\r",
                                    flush=True
                                )
                                time.sleep(1)

                            claim = self.claim_tasks(token, task_id, proxy)
                            if claim and claim['state'] == 'COMPLETED':
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {task['points']} GM {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}            "
                                )
                            time.sleep(3)

                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}Isn't Started{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        time.sleep(3)

                    elif task and status == 'CLAIMABLE':
                        claim = self.claim_tasks(token, task_id, proxy)
                        if claim and claim['state'] == 'COMPLETED':
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['points']} GM {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        time.sleep(3)

                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )

    def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                time.sleep(1)
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

                if use_proxy and use_proxy_choice == 1:
                    self.load_auto_proxies()
                elif use_proxy and use_proxy_choice == 2:
                    self.load_manual_proxy()

                for query in queries:
                    query = query.strip()
                    if query:
                        self.process_query(query, use_proxy)
                        self.log(f"{Fore.CYAN+Style.BRIGHT}-{Style.RESET_ALL}"*75)
                        seconds = random.randint(5, 10)
                        while seconds > 0:
                            formatted_time = self.format_seconds(seconds)
                            print(
                                f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT}Processing Next Accounts...{Style.RESET_ALL}",
                                end="\r",
                                flush=True
                            )
                            time.sleep(1)
                            seconds -= 1

                seconds = 86400
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Midas RWA - BOT.{Style.RESET_ALL}                                      ")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = MidasRWA()
    bot.main()
