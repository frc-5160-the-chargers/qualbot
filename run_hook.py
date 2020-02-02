import sys

from hooks.match_announce import MatchAnnouncementHookDiscord, MatchAnnouncementHookSlack

config_file = "config.json"

def run_queuing_lady_discord():
    queuing_lady = MatchAnnouncementHookDiscord(config_file=config_file)
    queuing_lady.send()

def run_queuing_lady_slack():
    queuing_lady = MatchAnnouncementHookSlack(config_file=config_file)
    queuing_lady.send()

def run_queuing_lady():
    run_queuing_lady_discord()
    run_queuing_lady_slack()

def main():
    available_hooks = ["", "queuing-lady-discord", "queuing-lady-slack", "queuing-lady"]
    if len(sys.argv) != 2 or sys.argv[1] not in available_hooks:
        print("Make sure the hook entered is valid")
        print("Configured hooks:", end="")
        print("\n  * ".join(available_hooks))
        return
    hook_running = sys.argv[1]
    # run the hook
    if hook_running in ["queuing-lady-discord"]:
        run_queuing_lady_discord()
        return
    if hook_running in ["queuing-lady-slack"]:
        run_queuing_lady_slack()
        return
    if hook_running in ["queuing-lady"]:
        run_queuing_lady()
        return

if __name__ == "__main__":
    main()
