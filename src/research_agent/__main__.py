from __future__ import annotations

import argparse
import logging
import sys

from research_agent.config import AppConfig
from research_agent.delivery.email import send_email
from research_agent.pipeline import collect_candidates, run_pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research_agent")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full daily pipeline.")
    run_parser.add_argument("--dry-run", action="store_true", help="Generate reports but do not send email.")
    run_parser.add_argument("--skip-llm", action="store_true", help="Collect and render candidates without calling LLMs.")

    collect_parser = subparsers.add_parser("collect", help="Collect candidates and print a summary.")
    collect_parser.add_argument("--limit", type=int, default=20)

    email_parser = subparsers.add_parser("test-email", help="Send a small SMTP test email.")
    email_parser.add_argument("--subject", default="Research Agent SMTP Test")

    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(name)s: %(message)s")
    config = AppConfig.from_env()

    try:
        if args.command == "run":
            if args.dry_run:
                config.send_email = False
            result = run_pipeline(config, dry_run=args.dry_run, skip_llm=args.skip_llm)
            print(f"Report written: {result.markdown_path}")
            print(f"JSON written: {result.json_path}")
            print(f"HTML written: {result.html_path}")
            if result.pdf_path:
                print(f"PDF written: {result.pdf_path}")
            print(f"Email sent: {result.email_sent}")
            return 0

        if args.command == "collect":
            candidates = collect_candidates(config)
            print(f"Collected {len(candidates)} candidates")
            for candidate in candidates[: args.limit]:
                print(f"- [{candidate.source}] {candidate.title} <{candidate.url}>")
            return 0

        if args.command == "test-email":
            config.validate_email()
            send_email(
                smtp=config.smtp_config(),
                subject=args.subject,
                body_markdown="Research agent SMTP test succeeded.",
                sender=config.email_from,
                recipients=config.email_to,
            )
            print("Test email sent")
            return 0
    except Exception as exc:
        logging.exception("Command failed: %s", exc)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
