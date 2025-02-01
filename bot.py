from curl_cffi import requests
from urllib.parse import parse_qs, unquote
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MidasRWA:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://prod-tg-app.midas.app',
            'Referer': 'https://prod-tg-app.midas.app/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random
        }
        self.source = 'ref_b6243c03-25ae-43f0-9667-5defd6c43b9b'
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

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
    
    def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
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
    
    def load_account_data(self, query: str):
        account = parse_qs(query).get('user', [None])[0]
        if account:
            account_data = json.loads(unquote(account))
            user_id = account_data["id"]
            name = account_data.get("first_name", "Unknown")
            return user_id, name
        else:
            raise ValueError("query_id invalid")
        
    def print_message(self, action, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}{action}:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
        )
    
    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    def user_login(self, query: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/auth/register'
        data = json.dumps({'initData':query, 'source':self.source})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="safari15_5")
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                
                self.print_message("Status    ", Fore.RED, 
                    f"Login Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                self.print_message("Proxy     ", Fore.WHITE, proxy)
                return None

    def user_data(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/user'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("Balance   ", Fore.RED, 
                    f"GET Data Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    def user_visited(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/user/visited'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.patch(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return None
                
    def daily_checkin(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/streak'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("Check-In  ", Fore.RED, 
                    f"GET Data Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                
    def claim_checkin(self, token: str, streak_days: int, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/streak'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("Check-In  ", Fore.WHITE, 
                    f"Day {streak_days}"
                    f"{Fore.RED+Style.BRIGHT} Isn't Claimed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                
    def refferal_status(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/referral/status'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("Refferal  ", Fore.RED, 
                    f"GET Data Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                
    def claim_refferal(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/referral/claim'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("Refferal  ", Fore.RED, 
                    f"Isn't Claimed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    def play_game(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/game/play'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("    > Tap-Tap", Fore.RED, 
                    f"Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    def available_tasks(self, token: str, proxy=None, retries=5):
        url = 'https://api-tg-app.midas.app/api/tasks/available'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.get(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue

                return self.print_message("Task Lists", Fore.RED, {str(e)})
            
    def perform_tasks(self, token: str, task_id: str, title: str, proxy=None, retries=5):
        url = f'https://api-tg-app.midas.app/api/tasks/start/{task_id}'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                if response.status_code == 400:
                    return self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                        f"{Fore.RED+Style.BRIGHT} Isn't Started: {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Not Eligible{Style.RESET_ALL}"
                    )
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue

                return self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                    f"{Fore.RED+Style.BRIGHT} Isn't Started: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    def claim_tasks(self, token: str, task_id: str, title: str, proxy=None, retries=5):
        url = f'https://api-tg-app.midas.app/api/tasks/claim/{task_id}'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': '0',
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = requests.post(url=url, headers=headers, proxy=proxy, timeout=60, impersonate="safari15_5")    
                if response.status_code == 400:
                    return self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                        f"{Fore.RED+Style.BRIGHT} Isn't Claimed: {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Not Eligible{Style.RESET_ALL}"
                    )
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue

                return self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                    f"{Fore.RED+Style.BRIGHT} Isn't Claimed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    def process_query(self, query: str, user_id: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
        token = None
        while token is None:
            token = self.user_login(query, proxy)
            if not token:
                proxy = self.rotate_proxy_for_account(user_id) if use_proxy else None
                time.sleep(1)
                continue

            self.print_message("Status    ", Fore.GREEN, "Login Success")
            self.print_message("Proxy     ", Fore.WHITE, proxy)

            user = self.user_data(token, proxy)
            if user:
                balance = user.get("points", 0)
                ticket = user.get("tickets", 0)

                first_visit = user.get("isFirstVisit", False)
                if first_visit:
                    self.user_visited(token, proxy)

                self.print_message("Balance   ", Fore.WHITE, f"{balance} GM")
                self.print_message("Ticket    ", Fore.WHITE, f"{ticket} Tap")

            checkin = self.daily_checkin(token, proxy)
            if checkin:
                streak_days = checkin.get("streakDaysCount", 0)
                is_claimable = checkin.get("claimable", False)

                if is_claimable:
                    claim = self.claim_checkin(token, streak_days, proxy)

                    if claim:
                        balance_reward = claim.get("nextRewards", {}).get("points", 0)
                        ticket_reward = claim.get("nextRewards", {}).get("tickets", 0)
                        self.print_message("Check-In  ", Fore.WHITE, 
                            f"Day {streak_days}"
                            f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{balance_reward} GM{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ticket_reward} Tap{Style.RESET_ALL}"
                        )

                else:
                    self.print_message("Check-In  ", Fore.WHITE, 
                        f"Day {streak_days} "
                        f"{Fore.YELLOW+Style.BRIGHT}Is Already Claimed{Style.RESET_ALL}"
                    )

            refferal = self.refferal_status(token, proxy)
            if refferal:
                can_claim = refferal.get("canClaim", False)

                if can_claim:
                    claim = self.claim_refferal(token, proxy)

                    if claim:
                        balance_reward = claim.get("totalPoints", 0)
                        ticket_reward = claim.get("totalTickets", 0)
                        self.print_message("Check-In  ", Fore.GREEN, f"Is Claimed "
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{balance_reward} GM{Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{ticket_reward} Tap{Style.RESET_ALL}"
                        )

                else:
                    self.print_message("Refferal  ", Fore.YELLOW, "No Available Reward")

            tickets = user.get("tickets", 0)
            user = self.user_data(token, proxy)
            if user:
                tickets = user.get("tickets", 0)

            if tickets > 0:
                self.print_message("Play Game ", Fore.GREEN, 
                    f"Available "
                    f"{Fore.WHITE+Style.BRIGHT}{ticket} Ticket{Style.RESET_ALL}"
                )

                while tickets > 0:
                    tap_tap = self.play_game(token, proxy)
                    if tap_tap: 
                        tickets -= 1
                        reward = tap_tap.get("points", 0)
            
                        self.print_message("    > Tap-Tap", Fore.GREEN, 
                            f"Success"
                            f"{Fore.WHITE+Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT}Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {reward} GM {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Ticket {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{tickets} Left{Style.RESET_ALL}"
                        )
                    else:
                        break

                    time.sleep(1)

            else:
                self.print_message("Play Game ", Fore.YELLOW, 
                    f"No Available Ticket"
                )

            tasks = self.available_tasks(token, proxy)
            if tasks:
                self.print_message("Task Lists", Fore.GREEN, "Available "
                    f"{Fore.WHITE+Style.BRIGHT}{len(tasks)} Tasks{Style.RESET_ALL}"
                )

                for task in tasks:
                    if task:
                        task_id = task.get('id')
                        title = task.get('name')
                        reward = task.get("points", 0)
                        delay = task.get('waitTime')
                        status = task.get('state')

                        if status == "COMPLETED":
                            self.print_message("    > Title  ", Fore.WHITE, f"{title} "
                                f"{Fore.YELLOW+Style.BRIGHT}Is Already Completed{Style.RESET_ALL}"
                            )
                            continue

                        if status == "WAITING":
                            start = self.perform_tasks(token, task_id, title, proxy)

                            if start and start.get('state') == "CLAIMABLE":
                                self.print_message("    > Title  ", Fore.WHITE, f"{title} "
                                    f"{Fore.GREEN+Style.BRIGHT}Is Started{Style.RESET_ALL}"
                                )

                                if delay is not None:
                                    for remaining in range(delay, 0, -1):
                                        print(
                                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT}    > Wait For{Style.RESET_ALL}"
                                            f"{Fore.YELLOW + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}Seconds to Claim Reward...{Style.RESET_ALL}",
                                            end="\r",
                                            flush=True
                                        )
                                        time.sleep(1)

                                claim = self.claim_tasks(token, task_id, title, proxy)
                                if claim and claim.get('state') == "COMPLETED":
                                    self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                                        f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT} Reward {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}"
                                    )

                            time.sleep(1)
                            
                        elif status == "CLAIMABLE":
                            claim = self.claim_tasks(token, task_id, title, proxy)
                            if claim and claim.get('state') == "COMPLETED":
                                self.print_message("    > Title  ", Fore.WHITE, f"{title}"
                                    f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT} Reward {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{reward} GM{Style.RESET_ALL}"
                                )

                            time.sleep(1)


    def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

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
                    self.load_proxies(use_proxy_choice)

                separator = "=" * 15
                for query in queries:
                    if query:
                        user_id, name = self.load_account_data(query)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {name} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        self.process_query(query, user_id, use_proxy)
                        time.sleep(3)

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
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Midas RWA - BOT.{Style.RESET_ALL}                                      ")
            return
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = MidasRWA()
    bot.main()