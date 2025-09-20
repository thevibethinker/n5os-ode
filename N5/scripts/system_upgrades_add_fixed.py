    def _rewrite_jsonl(self, items: List[Dict]) -> None:
        """Rewrite the entire JSONL file."""
        with open(self.jsonl_path, "w", encoding="utf-8") as f:
            for item in items:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")