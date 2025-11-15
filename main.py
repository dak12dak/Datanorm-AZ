import json
from pathlib import Path

import config
from datanorm_parser import parse_args
from datanorm_processor import DatanormProcessor
from json_formatter import align_json_colons


def main() -> None:
    args = parse_args()
    processor = DatanormProcessor()
    processor.load_file(args.file)

    # Determine action based on flags
    if args.export:
        # If export path is relative, prepend default output folder
        export_path = args.export
        if not export_path.is_absolute():
            output_folder = Path(config.default_output_folder)
            export_path = output_folder / export_path
            # Create output folder if it doesn't exist
            export_path.parent.mkdir(parents=True, exist_ok=True)
        # Export mode
        if args.article:
            processor.export_prices_to_csv(
                export_path, overhead_percent=args.overhead, article_no=args.article, quantity=args.quantity
            )
        elif args.prices:
            processor.export_prices_to_csv(
                export_path, overhead_percent=args.overhead, article_no=args.prices, quantity=args.quantity
            )
        else:
            # For export, use limit as specified (use --limit all for unlimited)
            processor.export_prices_to_csv(
                export_path, overhead_percent=args.overhead, limit=args.limit, quantity=args.quantity
            )
        print(f"Exported results to {export_path}")

    elif args.article:
        # Article lookup mode (raw data)
        article = processor.lookup_article(args.article)
        if not article:
            raise SystemExit(f"\nArticle {args.article} not found\n")
        json_output = json.dumps(article, ensure_ascii=False, indent=2)
        print(align_json_colons(json_output))

    elif args.prices:
        # Prices lookup mode (calculated prices for specific article)
        prices = processor.calculate_prices(
            overhead_percent=args.overhead, article_no=args.prices, quantity=args.quantity
        )
        if not prices:
            raise SystemExit(f"\nArticle {args.prices} not found\n")
        json_output = json.dumps(prices, ensure_ascii=False, indent=2)
        print(align_json_colons(json_output))

    elif args.limit == 1:
        # Default mode: first article with both article info and prices
        article_no = processor.get_first_article_no()
        if article_no:
            article = processor.lookup_article(article_no)
            prices = processor.calculate_prices(
                overhead_percent=args.overhead, article_no=article_no, quantity=args.quantity
            )
            result = {
                "article": article,
                "prices": prices[0] if prices else None,
            }
            json_output = json.dumps(result, ensure_ascii=False, indent=2)
            print(align_json_colons(json_output))
        else:
            print("[]")

    else:
        # List mode: multiple articles with calculated prices
        prices = processor.calculate_prices(
            overhead_percent=args.overhead, limit=args.limit, quantity=args.quantity
        )
        json_output = json.dumps(prices, ensure_ascii=False, indent=2)
        print(align_json_colons(json_output))


if __name__ == "__main__":
    main()


