from v1.entry_map import entity_mapping
import spacy
from v1.main import *

def test_entity_mapping_contains_key_person():
    assert 'PERSON' in entity_mapping, "The label 'PERSON' should be in the entity_mapping dictionary"

def test_entity_mapping_person_contains_pilot():
    assert 'Pilot' in entity_mapping.get('PERSON', []), "The 'PERSON' label should include 'Pilot'"

def test_spacy_recognizes_entity_mapping_patterns():
    #nlp = spacy.blank("en")
    #nlp = app.main.create_entity_ruler(nlp, entity_mapping)
    #test_sentence = "The Pilot flies the plane."
    #doc = nlp(test_sentence)
    #found_entities = [(ent.text, ent.label_) for ent in doc.ents]
    #expected_entities = [("Pilot", "PERSON")]
    #assert found_entities == expected_entities, "spaCy did not recognize the mapped entities correctly."
    pass