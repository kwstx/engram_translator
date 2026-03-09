from owlready2 import get_ontology, World, Thing
import os
import logging
import jsonschema
from pyDatalog import pyDatalog
pyDatalog.create_terms('X, Y, map_field')

logger = logging.getLogger(__name__)

class SemanticMapper:
    def __init__(self, ontology_path: str = None):
        """
        Initialize the SemanticMapper.
        :param ontology_path: Absolute or relative path to the OWL file.
        """
        self.world = World()
        self.ontology_path = ontology_path
        self.ontology = None
        
        if ontology_path:
            self.load_ontology(ontology_path)

    def load_ontology(self, path: str):
        """
        Loads an OWL ontology file using Owlready2.
        """
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            logger.error(f"Ontology file not found at {abs_path}")
            raise FileNotFoundError(f"Ontology file not found at {abs_path}")
        
        try:
            # Owlready2 expects 'file://' prefix for local files
            self.ontology = self.world.get_ontology(f"file://{abs_path}").load()
            logger.info(f"Successfully loaded ontology from {abs_path}")
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise

    def resolve_equivalent(self, concept: str, source_protocol: str) -> str:
        """
        Searches the ontology for synonyms or equivalents in target protocols.
        """
        if not self.ontology:
            return f"Error: Ontology not loaded."

        namespaces = {
            "A2A": "http://agent.middleware.org/A2A#",
            "MCP": "http://agent.middleware.org/MCP#",
            "ACP": "http://agent.middleware.org/ACP#",
            "BASE": "http://agent.middleware.org/protocols.owl#"
        }

        if source_protocol not in namespaces:
            return f"Error: Unknown protocol '{source_protocol}'"

        target_iri = f"{namespaces[source_protocol]}{concept}"
        source_concept = self.world.search_one(iri=target_iri)
        
        if not source_concept:
            source_concept = self.world.search_one(name=concept)
            if not source_concept:
                return f"Concept '{concept}' not found."

        equivalents = []
        if hasattr(source_concept, "equivalent_to"):
            for eq in source_concept.equivalent_to:
                if isinstance(eq, type):
                    equivalents.append(eq)
        
        for cls in self.world.classes():
            if source_concept in cls.equivalent_to:
                if cls not in equivalents:
                    equivalents.append(cls)

        if not equivalents:
            return f"No equivalents found for {source_protocol}:{concept}"

        for eq in equivalents:
            eq_iri = str(eq.iri)
            for proto, ns in namespaces.items():
                if eq_iri.startswith(ns) and proto != source_protocol and proto != "BASE":
                    concept_name = eq_iri.replace(ns, "")
                    return f"{proto}:{concept_name}"

        return f"Equivalents found but none in target protocols: {[str(e.iri) for e in equivalents]}"

    def DataSiloResolver(self, source_data: dict, source_schema: dict, target_schema: dict, source_protocol: str, target_protocol: str) -> dict:
        """
        Resolves data silos by detecting schema differences, flattening nested objects,
        and renaming fields based on ontology mappings and PyDatalog rules.
        """
        logger.info(f"Resolving data silo from {source_protocol} to {target_protocol}")

        # 1. JSON Schema Validation
        try:
            jsonschema.validate(instance=source_data, schema=source_schema)
            logger.info("Source data validated successfully.")
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            raise ValueError(f"Invalid source data: {e.message}")

        # 2. Flatten Nested Objects
        flattened_data = self._flatten_dict(source_data)
        logger.debug(f"Flattened data: {flattened_data}")

        # 3. Dynamic Mapping via PyDatalog Rules
        # Initialize logic for field mapping (clear previous rules)
        pyDatalog.clear()
        
        # Example rule: if source has user_info.name, map it to profile.fullname
        # This can be dynamically extended based on the ontology
        + map_field('user_info.name', 'profile.fullname')
        + map_field('payload.timestamp', 'data_bundle.iso_date')

        # 4. Resolve field names using Ontology Mappings
        mapped_data = {}
        for flat_key, value in flattened_data.items():
            # Check PyDatalog rules first
            res = map_field(flat_key, Y)
            if res:
                target_key = str(res[0][0])
                logger.info(f"PyDatalog mapping: {flat_key} -> {target_key}")
            else:
                # Fallback to SemanticMapper.resolve_equivalent if it's a single concept
                # This logic assumes the leaf key part is a concept
                leaf_key = flat_key.split('.')[-1]
                semantic_res = self.resolve_equivalent(leaf_key, source_protocol)
                
                if target_protocol in semantic_res:
                    target_key = semantic_res.split(':')[-1]
                    logger.info(f"Ontology mapping: {flat_key} -> {target_key}")
                else:
                    target_key = flat_key # Default to same name
            
            mapped_data[target_key] = value

        # 5. Reconstruct structure based on target_schema (simple version)
        # For now, we return the mapped data as is or nested if needed
        return mapped_data

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Recursively flattens a nested dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    try:
        mapper = SemanticMapper("app/semantic/protocols.owl")
        result = mapper.resolve_equivalent("task_handoff", "A2A")
        print(f"Mapping A2A:task_handoff -> {result}")
    except Exception as e:
        print(f"Test failed: {e}")
