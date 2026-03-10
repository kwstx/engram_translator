import argparse
import cProfile
import os
import pstats
from app.semantic.mapper import SemanticMapper


def run_profile(
    ontology_path: str,
    concept: str,
    source_protocol: str,
    iterations: int,
    use_resolver: bool,
) -> None:
    mapper = SemanticMapper(ontology_path)

    def workload():
        if use_resolver:
            source_data = {
                "user_info": {"name": "John Doe", "email": "john@example.com"},
                "payload": {"timestamp": "2024-03-20T10:00:00Z"},
            }
            source_schema = {
                "type": "object",
                "properties": {
                    "user_info": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                        },
                    },
                    "payload": {
                        "type": "object",
                        "properties": {"timestamp": {"type": "string"}},
                    },
                },
                "required": ["user_info", "payload"],
            }
            target_schema = {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "properties": {"fullname": {"type": "string"}},
                    }
                },
            }
            for _ in range(iterations):
                mapper.DataSiloResolver(
                    source_data,
                    source_schema,
                    target_schema,
                    source_protocol=source_protocol,
                    target_protocol="MCP",
                )
        else:
            for _ in range(iterations):
                mapper.resolve_equivalent(concept, source_protocol)

    profiler = cProfile.Profile()
    profiler.runcall(workload)
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(30)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile SemanticMapper with cProfile.")
    parser.add_argument(
        "--ontology",
        default=os.path.abspath("app/semantic/protocols.owl"),
        help="Path to ontology file.",
    )
    parser.add_argument("--concept", default="task_handoff", help="Concept to resolve.")
    parser.add_argument("--source-protocol", default="A2A", help="Protocol namespace.")
    parser.add_argument(
        "--iterations", type=int, default=200, help="Number of iterations."
    )
    parser.add_argument(
        "--resolver",
        action="store_true",
        help="Profile DataSiloResolver instead of resolve_equivalent.",
    )
    args = parser.parse_args()

    run_profile(
        ontology_path=args.ontology,
        concept=args.concept,
        source_protocol=args.source_protocol,
        iterations=args.iterations,
        use_resolver=args.resolver,
    )


if __name__ == "__main__":
    main()
