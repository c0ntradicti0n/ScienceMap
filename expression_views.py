from littletools.generator_tools import generate_new_string
from littletools.nested_list_tools import flatten_reduce, flatten

variable_generator = generate_new_string()

class forward_mapping_neo4j_view:
    def neo4j_write(self):
        if isinstance(self, dict):
            self.neo4j_name = 'bla'
            return [x.neo4j_write() for x in self.values() if hasattr(x, 'neo4j_write')]
        elif isinstance(self, list) or isinstance(self, tuple):
            return [x.neo4j_write() for x in self if hasattr(x, 'neo4j_write')]
        else:
            return ""


class argu_neo4j_view:
    def neo4j_write(self, ref_instead=True):
        global variable_generator
        self.neo4j_name=next(variable_generator)
        if not self.node_type:
            self.node_type = []
        if ref_instead:
            arg = self['coreferenced'](self['coref'])
            if not arg:
                arg = self
            else:
                arg = arg[0]
            return \
                """MERGE ( {my_name}:{node_type} {{id:{id}, s_id:{s_id}, text:'{text}', score:'{score}'}})\n""".format(
                    my_name=self.neo4j_name,
                    node_type=':'.join(self.node_type),
                    id=arg['id'],
                    s_id=self['s_id'],
                    i_s=self['i_s'],
                    score=str((self['subj_score'], self['aspe_score'])),
                    text=" ".join(arg['text']).replace("'", "")
                )
        return \
            """MERGE ( {my_name}:{node_type} {{id:{id}, s_id:{s_id}, text:'{text}', score:'{score}'}})\n""".format(
                my_name=self.neo4j_name,
                node_type=':'.join(self.node_type),
                id   = self['id'],
                s_id = self['s_id'],
                i_s  = self['i_s'],
                score = str((self['subj_score'], self['aspe_score'])),
                text = " ".join(self['text']).replace("'", "")
                )


class pred_neo4j_view:
    def neo4j_write(self, write_arguments=True):
        ''' Push results in nested iterables to neo4j

        :param write_arguments:
        :return:

        '''
        global variable_generator
        self.neo4j_name=next(variable_generator)

        if not hasattr(self, 'node_type'):
            self.node_type = ['NO_NODE_TYPE_ATTRIBUTE_AT_ALL']
        elif not self.node_type:
            self.node_type = ['NO_NODE_TYPE_SET']

        if write_arguments:
            arguments = [self['arguments'].neo4j_write()]
            argument_node_name = self['arguments'].neo4j_name
        else:
            arguments = ""

        return \
                ["""MERGE ({my_name}:{node_type} {{ id:{id}, s_id:{s_id}, text:'{text}' }})\n""".format(
                my_name=self.neo4j_name,
                node_type=':'.join(self.node_type),
                id   = self['id'],
                s_id = self['s_id'],
                i_s  = self['i_s'],
                text = " ".join(self['text']).replace("'", "")
                ), arguments,
                """MERGE ({my_name})-[:METHEXIS]->({argument_node_name}) \n""".format(
                my_name=self.neo4j_name,
                argument_node_name=argument_node_name)]


class iterable_neo4j_view:
    def __init__(self):
        pass

    def neo4j_write(self):
        global variable_generator
        self.neo4j_name = next(variable_generator)
        try:
            childrens_births = [n.neo4j_write() for n in self if hasattr(n, 'neo4j_write')]
        except:
            raise
        try:
            names = [n.neo4j_name for n in self if hasattr(n, 'neo4j_name')]
        except:
            raise
        if hasattr(self, 'type'):
            type = self.type
        else:
            type = 'unknown'
        if hasattr(self, 'reason'):
            reason = self.reason
        else:
            reason = 'unknown'

        if not hasattr(self, 'node_type'):
            self.node_type = ["node_type_not_given"]

        create_me = """MERGE ({my_name}:{node_type} {{Var:'{my_name}'}}) """.format(
            my_name=self.neo4j_name,
            node_type=':'.join(flatten(self.node_type))
            )

        return  [childrens_births,
                 [create_me],
                 ["""MERGE ({my_name})-[:X]->({x}) """.format(
                  my_name=self.neo4j_name,
                  x=x, type=type,
                  utype=type.upper(),
                  reason=reason)
                  for x in names]]

