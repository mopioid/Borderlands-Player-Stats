from unrealsdk import Log, GetEngine
from unrealsdk import RunHook, RemoveHook, UObject, UFunction, FStruct
from Mods import ModMenu

import re
from typing import Dict, Sequence


def _stats_requested(args: Sequence[str]) -> None:
    pc = GetEngine().GamePlayers[0].Actor
    if pc.GetPrimaryPlayerStandIn():
        Log("Stats are only available while in-game.")
        return

    if not args:
        Log("Please specify a keyword to search stats for, e.g.: stats chests")
        return

    try:
        pattern = re.compile(args[0], flags=re.I)
    except re.error:
        Log("Could not parse search pattern")
        return

    stats = pc.PlayerStats.StatProperties
    for stat in stats:
        name = str(stat.Id)[5:]
        if re.search(pattern, name):
            if stat.Data.Value2 and stat.Data.Value2.Dummy != 0:
                Log(f"{name}: {stat.Data.Value2}")
            else:
                Log(f"{name}: {stat.Data.Value1:,}")


try:
    from Mods import CommandExtensions

    try:
        CommandExtensions.UnregisterConsoleCommand("stats")
    except Exception:
        pass

    CommandExtensions.RegisterConsoleCommand(
        name="stats",
        callback=lambda args: _stats_requested(args),
        splitter=lambda args: [args],
    ).add_argument("keywords")

except ImportError:

    def _console_command(_c: UObject, _f: UFunction, params: FStruct) -> bool:
        command, *args = params.Command.split(maxsplit=1)
        if command != "stats":
            return True
        _stats_requested(args)
        return False

    RemoveHook(
        "Engine.PlayerController.ConsoleCommand",
        "PlayerStats",
    )
    RunHook(
        "Engine.PlayerController.ConsoleCommand",
        "PlayerStats",
        _console_command,
    )


class PlayerStats(ModMenu.SDKMod):
    Name: str = "Player Stats"
    Version: str = "1.0"
    Description: str = (
        "Use the console to find stats about the current save file.\n\n"
        "To use, open your console, and type:\n"
        "stats &lt;keyword&gt;"
    )
    Author: str = "mopioid"
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Utility

    Status: str = '<font color="#00FF00">Loaded</font>'
    SettingsInputs: Dict[str, str] = {}


_mod_instance = PlayerStats()

if __name__ == "__main__":
    for mod in ModMenu.Mods:
        if mod.Name == _mod_instance.Name:
            ModMenu.Mods.remove(mod)
            _mod_instance.__class__.__module__ = mod.__class__.__module__
            break

ModMenu.RegisterMod(_mod_instance)
