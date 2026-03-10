import argparse
import os
from datetime import datetime, timedelta, timezone

import jwt


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a JWT for local testing.")
    parser.add_argument("--issuer", default=os.getenv("AUTH_ISSUER", "https://auth.local/"))
    parser.add_argument("--audience", default=os.getenv("AUTH_AUDIENCE", "translator-middleware"))
    parser.add_argument("--subject", default="test-user")
    parser.add_argument("--scope", action="append", default=["translate:a2a"])
    parser.add_argument("--expires-minutes", type=int, default=60)
    parser.add_argument("--algorithm", default=os.getenv("AUTH_JWT_ALGORITHM", "HS256"))
    parser.add_argument("--secret", default=os.getenv("AUTH_JWT_SECRET"))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.algorithm.startswith("HS") and not args.secret:
        raise SystemExit("AUTH_JWT_SECRET is required for HS* algorithms.")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": args.subject,
        "iss": args.issuer,
        "aud": args.audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=args.expires_minutes)).timestamp()),
        "scope": " ".join(args.scope),
    }

    token = jwt.encode(payload, args.secret, algorithm=args.algorithm)
    print(token)


if __name__ == "__main__":
    main()
