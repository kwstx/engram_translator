from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF, XSD
from typing import Optional, List, Dict
import os

class OntologyManager:
    def __init__(self):
        self.graph = Graph()
        self.default_namespace = "http://agent.middleware.org/"

    def load_ontology(self, source: str, format: str = "xml"):
        """Loads an ontology from a file or string."""
        if os.path.exists(source):
            self.graph.parse(source, format=format)
        else:
            self.graph.parse(data=source, format=format)

    def add_mapping(self, source_term: str, target_term: str, predicate: str = "sameAs"):
        """Adds a mapping link between two terms."""
        s = URIRef(f"{self.default_namespace}{source_term}")
        p = URIRef(f"http://www.w3.org/2002/07/owl#{predicate}")
        o = URIRef(f"{self.default_namespace}{target_term}")
        self.graph.add((s, p, o))

    def resolve_mapping(self, source_term: str) -> List[str]:
        """Resolves a term to its mapped equivalents."""
        s = URIRef(f"{self.default_namespace}{source_term}")
        p = URIRef("http://www.w3.org/2002/07/owl#sameAs")
        mappings = []
        for o in self.graph.objects(s, p):
            mappings.append(str(o).replace(self.default_namespace, ""))
        return mappings

    def get_rdf_xml(self) -> str:
        """Serializes the graph to RDF/XML."""
        return self.graph.serialize(format="xml")

ontology_manager = OntologyManager()
