"""Calculation of statistics related to dependency distance"""
from spacy.tokens import Doc, Token, Span
from spacy.language import Language

import numpy as np


@Language.factory("dependency_distance")
def create_dependency_distance_component(nlp: Language, name: str):
    return DependencyDistance(nlp)


class DependencyDistance:
    def __init__(self, nlp: Language):
        """Initialise components"""
        if not Token.has_extension("dependency_distance"):
            Token.set_extension("dependency_distance", getter=self.token_dependency)
        if not Span.has_extension("dependency_distance"):
            Span.set_extension("dependency_distance", getter=self.span_dependency)
        if not Doc.has_extension("dependency_distance"):
            Doc.set_extension("dependency_distance", getter=self.doc_dependency)

    def __call__(self, doc: Doc):
        """Run the pipeline component"""
        return doc

    def token_dependency(self, token: Token):
        """Token-level dependency distance"""
        dep_dist = 0
        ajd_dep = False
        if token.dep_ != "ROOT":
            dep_dist = abs(token.head.i - token.i)
            if dep_dist == 1:
                ajd_dep = True
        return {"dependency_distance": dep_dist, "adjacent_dependency": ajd_dep}

    def span_dependency(self, span: Span):
        """Span-level aggregated dependency distance"""
        dep_dists, adj_deps = zip(
            *[token._.dependency_distance.values() for token in span]
        )
        return {
            "dependency_distance_mean": np.mean(dep_dists),
            "prop_adjacent_dependency_relation": np.mean(adj_deps),
        }

    def doc_dependency(self, doc: Doc):
        """Doc-level dependency distance aggregated on sentence level"""
        dep_dists, adj_deps = zip(
            *[sent._.dependency_distance.values() for sent in doc.sents]
        )
        return {
            "dependency_distance_mean": np.mean(dep_dists),
            "dependency_distance_std": np.std(dep_dists),
            "prop_adjacent_dependency_relation_mean": np.mean(adj_deps),
            "prop_adjacent_dependency_relation_std": np.std(adj_deps),
        }
