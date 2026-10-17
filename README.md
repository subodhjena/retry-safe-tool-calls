# Tool calls that can be retried safely

Create a local support task with tenant-scoped operation IDs and an atomic replay record. Reproduce a response lost after commit.

This is the runnable companion to [the article](https://subodhjena.com/blog/tool-calls-that-can-be-retried-safely). Website MDX is the canonical article; [article.md](article.md) is a deliberate GitHub-readable snapshot. Code and fixtures are canonical here. Research and examples updated on 17 October 2026.

## Reproduce

Python 3.11 or later, standard library only. No API keys, packages, or network access. Verified locally on Python 3.14.5.

```bash
python3 -m unittest -v
python3 operations.py
```

Compare stdout with [sample-output.txt](sample-output.txt). The tests exercise failure paths as well as the expected result. All fixtures are synthetic.

## Scope and limits

One SQLite database owns every durable effect. Trusted caller authentication/authorization is a precondition, not implemented here. No external API or distributed transaction. Operation records have no expiry in this demonstration. Failures are injected exceptions before and after commit, not power loss or process termination. Concurrent duplicate delivery is a correctness check with 16 requests and 8 threads, not a load benchmark.

## Supporting material

- [Source notes](references.md), with versions and claim boundaries.
- [Recorded output](sample-output.txt).
- [Article snapshot](article.md).

The tests validate this demonstration, not production readiness. Source papers and documentation remain under their original licenses. Original example code and article text in this repository use the [MIT license](LICENSE).
