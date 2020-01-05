import itertools

import neo4j
from more_itertools import flatten

from helpers.color_logger import *
import bio_annotation
import basic_nlp_annotator
import json


class Neo4JHandler:
    def __init__(self):
        self.graph = neo4j.Connector('http://localhost:7474', ("s0krates", "password"))
        self.graph.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

    def run(self, query):
        #query = query.replace(r"'", r"\'")
        try:
            print (query)
            return self.graph.run(query)
        except neo4j.Neo4jErrors as e:
            logging.error(str(e))
            return None


    def node_chain_to_merge(self, node_chain, nodes_declared=set(), layout=None, D_KIND='D'):
        if nodes_declared:
            x=1
        if layout=='structured_span':
            it = [(id, kind, tokens) for  kind, (id, end), tokens in node_chain]
        elif layout=='similarity_comp':
            it = [(d['id'], d['kind'], d['annotation_tokens']) for d in node_chain]
        else:
            raise ValueError('layout must be given!')

        nodes = [
            '(n{id}:{kind} {{Tokens:"{tokens}"}})'.format(id=id, kind=kind, tokens=' '.join([t[1][0] for t in tokens]))
            if id not in nodes_declared else
            '(n{start})'.format(id=id, kind=kind)
            for id, kind, tokens in it
            ]
        nodes_declared.update({start for kind, (start, end), tokens in node_chain})
        edges = (f"-[:{D_KIND}{{Kind:'{D_KIND}'}}]->").join(nodes)
        return "MERGE {edges}".format(edges=edges).strip()

    def node_chains_to_query(self, node_chains, nodes_declared=set(), D_KIND='D'):
        return "\n".join(self.node_chain_to_merge(nc, nodes_declared=nodes_declared, layout='similarity_comp', D_KIND=D_KIND) for nc in node_chains)

    def nodify_id(self, n):
        return "".join(['(n', str(n),')'])
    def attribute_to_property(self, n, KIND, val=None):
        if not val:
            p_key = KIND.title()
            p_value = n[KIND].lower()
        else:
            p_key = val
            p_value = KIND

        return  "".join(['%s' % p_key, ':', '"', p_value, '"'])
    def nodify(self, n, kind=None, tokens=None, yet_declared=set()):
        infos = []
        if n['id'] not in yet_declared:
            if kind:
                infos.extend([':', n['kind']])
            if tokens:
                infos.extend([' {', self.attribute_to_property(n, 'kind'), ', ', self.attribute_to_property(n, 'lemma_text'), ', ', self.attribute_to_property(n, 'text'),  '}'])
        yet_declared.add(n['id'])
        return "".join(['(n', str(n['id']), *infos, ')'])

    def edgify(self, nodes, KIND, info={}):
        if info:
            attrs = f" {{Kind:'{KIND}', %s}}" % (json.dumps(info))
        else:
            attrs = f"{{Kind:'{KIND}'}}"
        r = f"-[:%s%s]->" % (KIND, attrs)
        return r.join(nodes)

    def mergify(self, edges):
        return ['MERGE %s' % m for m in edges]

    def nlify(self, merges):
        return "\n".join(merges) + "\n"

    def rel_from_nested_trig(self, trig, R_KIND='X'):
        nodes = [("-[:%s {Kind:'%s'}]->" % (R_KIND, R_KIND), self.nodify_id(k1), self.nodify_id(k2)) for k1, d2 in trig.items() for k2, info in d2.items()]
        return "\n".join(["MERGE " + r.join([t1, t2]) for r, t1, t2 in nodes])

    def node_merges(self, nodes, yet_declared=set()):
        unique_nodes = []
        seen = []
        for n in nodes:
            if n['id'] not in seen:
                unique_nodes.append(n)
                seen.append(n['id'])
        return  self.nlify(self.mergify([self.nodify(n, kind=True, tokens=True, yet_declared=yet_declared) for n in unique_nodes]))

    def edge_merges(self, *args, **kwargs):
        connector_nodes, merges = self._edge_merges(*args, **kwargs)
        connections = '' # self.connect_nodes(connector_nodes, D_KIND='C')
        return "".join(set(merges)) + connections
    def _edge_merges(self, complex, D_KIND='D', info=None):
        connector_nodes = []
        if not isinstance(complex[0], dict):
            ems = []

            for e in complex:
                new_connector_nodes, new_edges = self._edge_merges(e, D_KIND=D_KIND, info=info)
                ems.extend(new_edges)

                if new_connector_nodes:
                    connector_nodes.extend(new_connector_nodes)

            if len(connector_nodes)>=2:
                pass
                #connections_between = [self.connect_nodes(connector_nodes, D_KIND='C')]
                #ems.extend(connections_between)

            return [], ems
        else:
            return self.__edge_merges(complex, D_KIND=D_KIND, info=info)

    def __edge_merges(self, complex, D_KIND='D', info=None):
            nodes = [self.nodify(n, kind=False, tokens=False) for n in complex]
            #connector_node = [a['id'] for a in sorted(complex, key=lambda x: x['kind']]
            edges =  self.edgify(nodes,KIND=D_KIND )
            merges = self.mergify([edges])
            big_merge = self.nlify(merges)
            return nodes, [big_merge]
    def connect_nodes(self, connector_nodes, D_KIND='C'):
        connector_edges = self.edgify(connector_nodes, D_KIND)
        connector_merges = self.mergify([connector_edges])
        big_connector_merge = self.nlify(connector_merges)
        return big_connector_merge

    def level_merges(self, complex, kind=None, KIND='L'):
        level = [[annotation for side in diff for annotation in side if annotation['kind']==kind] for diffs in complex for diff in diffs]
        return self.nlify(self.mergify([self.edgify([self.nodify(n) for n in annotations], KIND=KIND) for annotations in level]))

    def relations_from_trigger(self, trigger, R_KIND='X'):
        merge = '\n'.join([self.rel_from_nested_trig(t, R_KIND=R_KIND) for tup in trigger for t in tup])
        return merge

    def nlp_complex_to_connect(self, complex, D_KIND='D', L_KIND='L', R_KIND='X'):
        nodes_declared = set()
        #chains = self.node_chains_to_query([flatten(flatten(l)) for l in complex], nodes_declared=nodes_declared, D_KIND=D_KIND)
        nodes = self.node_merges(list(flatten(flatten(flatten(complex)))), yet_declared=nodes_declared)
        def_rels   = self.edge_merges(complex, D_KIND=D_KIND)
        level_rels = self.level_merges(complex, kind='SUBJECT', KIND=L_KIND)
        comp_connection = self.relations_from_trigger(complex.trigger, R_KIND=R_KIND)
        commands = nodes + def_rels + level_rels + comp_connection
        return commands + """ RETURN 1 """

    def add_annotation(self, structured_span):
        chains = []
        f = lambda x: chains.append(x)
        bio_annotation.BIO_Annotation.apply_on_side(structured_span, f)
        bio_annotation.BIO_Annotation.apply_on_kinds(structured_span, f)
        query = self.node_chains_to_query(chains)
        print (query)
        self.run(query)

    def add_comparison_results (self, compared, D_KIND='D', L_KIND='L', R_KIND='X'):
        queries = [self.nlp_complex_to_connect(pairs, D_KIND=D_KIND, L_KIND=L_KIND, R_KIND=R_KIND) for pairs in compared]
        for q in queries:
            self.run(q)



