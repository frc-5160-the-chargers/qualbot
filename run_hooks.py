import sys

from hooks.match_announce import MatchAnnouncementHook

config_file = "config.json"

def run_queuing_lady():
    queuing_lady = MatchAnnouncementHook(config_file=config_file)
    queuing_lady.send()

def main():
    available_hooks = ["", "queuing-lady"]
    if len(sys.argv) != 2 or sys.argv[1] not in available_hooks:
        print("Make sure the hook entered is valid")
        print("Configured hooks:", end="")
        print("\n  * ".join(available_hooks))
        return
    hook_running = sys.argv[1]
    # run the hook
    if hook_running in ["queuing-lady"]:
        run_queuing_lady()
        return

if __name__ == "__main__":
    main()
