"""proof-registry CLI: serve | lookup | publish | emit."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from proof_engine_registry import __version__
from proof_engine_registry.client import RegistryClient
from proof_engine_registry.config import load_registries, Registry
from proof_engine_registry.emit import emit_registry_files
from proof_engine_registry.server import RegistryServer


def _cmd_serve(args) -> int:
    token = os.environ.get(args.token_env) if args.token_env else None
    srv = RegistryServer(
        proofs_dir=Path(args.proofs_dir),
        name=args.name,
        base_url=args.base_url or f"http://{args.bind}:{args.port}",
        bind=args.bind, port=args.port,
        auth_token=token,
    )
    if args.print_port_to:
        Path(args.print_port_to).write_text(str(srv.port))
    print(f"proof-registry serving {args.proofs_dir} on http://{args.bind}:{srv.port}",
          file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
    return 0


def _cmd_emit(args) -> int:
    emit_registry_files(
        proofs_dir=Path(args.proofs_dir),
        output_dir=Path(args.output_dir),
        base_url=args.base_url,
        registry_name=args.name,
        publishes_supported=False,
    )
    print(f"emitted registry to {args.output_dir}", file=sys.stderr)
    return 0


def _cmd_lookup(args) -> int:
    registries = load_registries()
    if not registries:
        print("error: no registries configured (expected ~/.config/proof-engine/registries.toml)",
              file=sys.stderr)
        return 2
    client = RegistryClient(registries)
    hit = client.lookup(args.claim)
    if hit is None:
        if args.json:
            sys.stdout.write(json.dumps({"hit": False}) + "\n")
        else:
            sys.stdout.write("no hit\n")
        return 1
    payload = asdict(hit.entry) | {"registry_name": hit.registry_name}
    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2 if args.pretty else None) + "\n")
    else:
        sys.stdout.write(f"{hit.registry_name}: {hit.slug} → {hit.proof_url}\n")
    return 0


def _cmd_publish(args) -> int:
    # Find the one publish target.
    registries = [r for r in load_registries() if r.publish]
    if not registries:
        print("error: no registry has publish = true", file=sys.stderr)
        return 2
    if len(registries) > 1:
        print("error: more than one registry has publish = true (blocked by config loader)",
              file=sys.stderr)
        return 2
    target = registries[0]
    body = json.loads(Path(args.proof_json).read_text())
    import requests
    r = requests.post(
        f"{target.url}/proofs",
        json={"slug": body["slug"], "claim": body["claim"], "proof_json": body},
        headers={"Authorization": f"Bearer {target.token}"} if target.token else {},
        timeout=30,
    )
    if r.status_code == 201:
        print(f"published {body['slug']} to {target.name}", file=sys.stderr)
        return 0
    print(f"publish failed: HTTP {r.status_code} {r.text}", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="proof-registry")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("serve", help="Run a self-hosted registry server.")
    s.add_argument("proofs_dir")
    s.add_argument("--name", default="Self-Hosted Proof Registry")
    s.add_argument("--base-url", default=None)
    s.add_argument("--bind", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8080)
    s.add_argument("--token-env", default=None,
                   help="Env var holding the bearer token required for publishing.")
    s.add_argument("--print-port-to", default=None,
                   help="Write the bound port to this file (for test orchestration).")
    s.set_defaults(func=_cmd_serve)

    e = sub.add_parser("emit", help="Emit static registry JSON from a proofs dir.")
    e.add_argument("proofs_dir")
    e.add_argument("output_dir")
    e.add_argument("--base-url", required=True)
    e.add_argument("--name", default="Proof Registry")
    e.set_defaults(func=_cmd_emit)

    l = sub.add_parser("lookup", help="Look up a claim across configured registries.")
    l.add_argument("claim")
    l.add_argument("--json", action="store_true")
    l.add_argument("--pretty", action="store_true")
    l.set_defaults(func=_cmd_lookup)

    pub = sub.add_parser("publish", help="Publish a proof.json to the publish-target registry.")
    pub.add_argument("proof_json")
    pub.set_defaults(func=_cmd_publish)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
