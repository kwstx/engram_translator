import pytest
import os
from app.semantic.ontology_manager import OntologyManager

def test_ontology_manager_init():
    om = OntologyManager()
    assert om.default_namespace == "http://agent.middleware.org/"
    assert len(om.graph) == 0

def test_ontology_manager_add_and_resolve():
    om = OntologyManager()
    om.add_mapping("source_test", "target_test")
    mappings = om.resolve_mapping("source_test")
    assert "target_test" in mappings
    assert len(mappings) == 1

def test_ontology_manager_load_from_string():
    om = OntologyManager()
    # Minimal RDF/XML string
    rdf_data = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:base="http://agent.middleware.org/">
  <owl:Class rdf:about="http://agent.middleware.org/TermA">
    <owl:sameAs rdf:resource="http://agent.middleware.org/TermB"/>
  </owl:Class>
</rdf:RDF>
"""
    om.load_ontology(rdf_data, format="xml")
    mappings = om.resolve_mapping("TermA")
    assert "TermB" in mappings

def test_ontology_manager_get_rdf_xml():
    om = OntologyManager()
    om.add_mapping("A", "B")
    xml = om.get_rdf_xml()
    assert "http://agent.middleware.org/A" in xml
    assert "http://agent.middleware.org/B" in xml
    assert "sameAs" in xml
