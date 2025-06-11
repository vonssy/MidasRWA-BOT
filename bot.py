from curl_cffi import requests
from urllib.parse import parse_qs, unquote
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MidasRWA:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://prod-tg-app.midas.app",
            "Referer": "https://prod-tg-app.midas.app/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
        }
        self.BASE_API = "https://api-tg-app.midas.app"
        self.ref_code = "ref_b6243c03-25ae-43f0-9667-5defd6c43b9b" # U can change it with yours.
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.query_id = {}
        self.username = {}
        self.tokens = {}

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
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, user_id):
        if user_id not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[user_id] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[user_id]

    def rotate_proxy_for_account(self, user_id):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[user_id] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def extract_query_data(self, query: str):
        try:
            account = parse_qs(query).get('user', [None])[0]
            account_data = json.loads(unquote(account))
            user_id = account_data.get("id", None)
            username = account_data.get("username", "Unknown")

            return user_id, username
        except Exception as e:
            return None, None
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxyscrape Free Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Proxyscrape Free" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def user_login(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/auth/register"
        data = json.dumps({"initData":self.query_id[user_id], "source":self.ref_code})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Access Token Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None

    async def user_data(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error     :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Balance & Tickets Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def user_visited(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/visited"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.patch, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error     :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Visited Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def daily_checkin(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/streak"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Status Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def claim_checkin(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/streak"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def refferal_status(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/referral/status"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Claimable Reward Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
                
    async def claim_refferal(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/referral/claim"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Reward Not Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def play_game(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/game/play"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                if response.status_code == 400:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   ●{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Tap-Tap {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                
        return None
            
    async def available_tasks(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/available"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Lists Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def perform_tasks(self, user_id: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/start/{task_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 400:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Start Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def claim_tasks(self, user_id: str, task_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/claim/{task_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.tokens[user_id]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110", verify=False)    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                
        return None
            
    async def process_user_login(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            token = await self.user_login(user_id, proxy)
            if token:
                self.tokens[user_id] = token

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} GET Access Token Success {Style.RESET_ALL}"
                )
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(user_id)
                await asyncio.sleep(5)
                continue

            return False
            
    async def process_accounts(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(user_id, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
            

            user = await self.user_data(user_id, proxy)
            if user:
                balance = user.get("points", 0)
                tickets = user.get("tickets", 0)
                first_visit = user.get("isFirstVisit", False)

                if first_visit:
                    await self.user_visited(user_id, proxy)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} GM {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Tickets   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tickets} Tap {Style.RESET_ALL}"
                )

            checkin = await self.daily_checkin(user_id, proxy)
            if checkin:
                streak_days = checkin.get("streakDaysCount", 0)
                is_claimable = checkin.get("claimable", False)

                if is_claimable:
                    claim = await self.claim_checkin(user_id, proxy)
                    if claim:
                        checkin_balance_reward = claim.get("nextRewards", {}).get("points", 0)
                        checkin_tickets_reward = claim.get("nextRewards", {}).get("tickets", 0)

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {streak_days} {Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin_balance_reward} GM {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}|{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {checkin_tickets_reward} Tap {Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} Day {streak_days} {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Already Claimed{Style.RESET_ALL}"
                    )

            refferal = await self.refferal_status(user_id, proxy)
            if refferal:
                can_claim = refferal.get("canClaim", False)

                if can_claim:
                    claim = await self.claim_refferal(user_id, proxy)
                    if claim:
                        ref_balance_reward = claim.get("totalPoints", 0)
                        ref_tickets_reward = claim.get("totalTickets", 0)

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ref_balance_reward} GM{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ref_tickets_reward} Tap{Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Referral  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Reward {Style.RESET_ALL}"
                    )
            
            user = await self.user_data(user_id, proxy)
            if user:
                tickets = user.get("tickets", 0)

                if tickets > 0:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Tap Games :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Available {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{tickets} Chances{Style.RESET_ALL}"
                    )

                    while tickets > 0:
                        tap_tap = await self.play_game(user_id, proxy)
                        if tap_tap: 
                            tap_reward = tap_tap.get("points", 0)
                            tickets -= 1

                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ●{Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT} Tap-Tap {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT}Reward:{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {tap_reward} GM {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}|{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {tickets} {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}Chances Left{Style.RESET_ALL}"
                            )
                        else:
                            break

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Tap Games :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Chances {Style.RESET_ALL}"
                    )

            tasks = await self.available_tasks(user_id, proxy)
            if tasks:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}")

                for task in tasks:
                    if task:
                        task_id = task.get("id")
                        title = task.get("name")
                        reward = task.get("points", 0)
                        delay = task.get("waitTime", 0)
                        status = task.get("state")

                        if status == "COMPLETED":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT} [Completed] {Style.RESET_ALL}"
                            )
                            continue

                        if status == "WAITING":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} [Waiting] {Style.RESET_ALL}"
                            )

                            start = await self.perform_tasks(user_id, task_id, proxy)
                            if start and start.get("state") == "CLAIMABLE":
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT}Start Status:{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                )

                                for remaining in range(delay, 0, -1):
                                    print(
                                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                        f"{Fore.YELLOW+Style.BRIGHT} Wait For {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{remaining}{Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT} Seconds to Claim Reward... {Style.RESET_ALL}",
                                        end="\r",
                                        flush=True
                                    )
                                    await asyncio.sleep(1)

                                claim = await self.claim_tasks(user_id, task_id, proxy)
                                if claim and claim.get("state") == "COMPLETED":
                                    self.log(
                                        f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}                                "
                                    )

                            
                        elif status == "CLAIMABLE":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT} [Claimable] {Style.RESET_ALL}"
                            )

                            claim = await self.claim_tasks(user_id, task_id, proxy)
                            if claim and claim.get("state") == "COMPLETED":
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT}Claim Status:{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}"
                                )

    async def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                
                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                separator = "=" * 20
                for idx, query in enumerate(queries, start=1):
                    if query:
                        user_id, username = self.extract_query_data(query)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(queries)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not user_id or not username:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Query Data {Style.RESET_ALL}"
                            )
                            continue

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Username  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
                        )

                        self.query_id[user_id] = query
                        self.username[user_id] = username
                        
                        await self.process_accounts(user_id, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*50)

                seconds = 12 * 60 * 60
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
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = MidasRWA()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Midas RWA - BOT{Style.RESET_ALL}                                       "                              
        )