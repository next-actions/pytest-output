from __future__ import annotations

import argparse
import json


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace: argparse.Namespace, values, option_string=None):
        if not hasattr(namespace, self.dest):
            setattr(namespace, self.dest, dict())

        if values is None:
            return

        property = getattr(namespace, self.dest)
        for item in values:
            if "=" not in item:
                raise argparse.ArgumentError(self, f'Expected key=value in {option_string}, got "{item}"')

            key, value = item.split("=", maxsplit=1)
            property[key] = value


class JSONAction(argparse.Action):
    def __call__(self, parser, namespace: argparse.Namespace, values, option_string=None):
        if not hasattr(namespace, self.dest):
            setattr(namespace, self.dest, dict())

        if values is None:
            return

        property = getattr(namespace, self.dest)
        for item in values:
            try:
                data = json.loads(item)
            except json.JSONDecodeError as e:
                raise argparse.ArgumentError(self, f'Invalid JSON format in {option_string}: "{str(e)}"')

            for key, value in data.items():
                if not isinstance(value, (str, int, float, bool)):
                    raise argparse.ArgumentError(
                        self, f'Expected scalar value for {key} in {option_string}, got "{str(value)}"'
                    )

                property[key] = value
