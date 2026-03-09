from owlready2 import get_ontology, World, Thing
import os
import logging

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
        Example: A2A:task_handoff owl:equivalentTo MCP:coord_transfer
        
        :param concept: The concept name (e.g., 'task_handoff')
        :param source_protocol: The protocol namespace (e.g., 'A2A')
        :return: The equivalent concept in a target protocol (e.g., 'MCP:coord_transfer')
        """
        if not self.ontology:
            return "Error: Ontology not loaded."

        # Namespaces mapping based on the ontology structure
        namespaces = {
            "A2A": "http://agent.middleware.org/A2A#",
            "MCP": "http://agent.middleware.org/MCP#",
            "ACP": "http://agent.middleware.org/ACP#",
            "BASE": "http://agent.middleware.org/protocols.owl#"
        }

        if source_protocol not in namespaces:
            return f"Error: Unknown protocol '{source_protocol}'"

        target_iri = f"{namespaces[source_protocol]}{concept}"
        
        # Search for the concept by IRI
        source_concept = self.world.search_one(iri=target_iri)
        
        if not source_concept:
            # Fallback: search by name regardless of namespace
            source_concept = self.world.search_one(name=concept)
            if not source_concept:
                return f"Concept '{concept}' not found."

        # Retrieve equivalent classes
        # Owlready2 stores them in the .equivalent_to attribute
        equivalents = []
        if hasattr(source_concept, "equivalent_to"):
            for eq in source_concept.equivalent_to:
                # eq can be a class or a complex logical expression
                if isinstance(eq, type): # It's a class
                    equivalents.append(eq)
        
        # Bi-directional search: check which other classes have source_concept as equivalent
        for cls in self.world.classes():
            if source_concept in cls.equivalent_to:
                if cls not in equivalents:
                    equivalents.append(cls)

        if not equivalents:
            return f"No equivalents found for {source_protocol}:{concept}"

        # Find the first equivalent that belongs to a different protocol
        for eq in equivalents:
            eq_iri = str(eq.iri)
            for proto, ns in namespaces.items():
                if eq_iri.startswith(ns) and proto != source_protocol and proto != "BASE":
                    concept_name = eq_iri.replace(ns, "")
                    return f"{proto}:{concept_name}"

        return f"Equivalents found but none in target protocols: {[str(e.iri) for e in equivalents]}"

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    try:
        mapper = SemanticMapper("app/semantic/protocols.owl")
        result = mapper.resolve_equivalent("task_handoff", "A2A")
        print(f"Mapping A2A:task_handoff -> {result}")
    except Exception as e:
        print(f"Test failed: {e}")
