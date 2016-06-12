from traceback import format_exception_only as feo

from nose.tools import assert_raises, eq_, ok_

from oemof.core.energy_system import EnergySystem as ES
from oemof.network import Bus, Node, Transformer


class Node_Tests:
    def test_that_attributes_cannot_be_added(self):
        node = Node()
        with assert_raises(AttributeError):
            node.foo = "bar"

    def test_symmetric_input_output_assignment(self):
        n1 = Node(label="<N1>")

        n2 = Node(label="<From N1>", inputs=[n1])
        ok_(n1 in n2.inputs,
            "{0} not in {1}.inputs, ".format(n1, n2) +
            "although it should be by construction.")
        ok_(n2 in n1.outputs,
            "{0} in {1}.inputs but {1} not in {0}.outputs.".format(n1, n2))

        n3 = Node(label="<To N1>", outputs=[n1])
        ok_(n1 in n3.outputs,
            "{0} not in {1}.outputs, ".format(n1, n3) +
            "although it should be by construction.")
        ok_(n3 in n1.inputs,
            "{0} in {1}.outputs but {1} not in {0}.inputs.".format(n1, n3))

    def test_accessing_outputs_of_a_node_without_output_flows(self):
        n = Node()
        exception = None
        try:
            outputs = n.outputs
        except Exception as e:
            exception = e
        ok_(exception is None,
            "\n  Test accessing `outputs` on {} having no outputs.".format(n) +
            "\n  Got unexpected exception:\n" +
            "\n      {}".format(feo(type(exception), exception)[0]))
        ok_(len(outputs) == 0,
            "\n  Failure when testing `len(outputs)`." +
            "\n  Expected: 0." +
            "\n  Got     : {}".format(len(outputs)))

    def test_accessing_inputs_of_a_node_without_input_flows(self):
        n = Node()
        exception = None
        try:
            inputs = n.inputs
        except Exception as e:
            exception = e
        ok_(exception is None,
            "\n  Test accessing `inputs` on {} having no inputs.".format(n) +
            "\n  Got unexpected exception:\n" +
            "\n      {}".format(feo(type(exception), exception)[0]))
        ok_(len(inputs) == 0,
            "\n  Failure when testing `len(inputs)`." +
            "\n  Expected: 0." +
            "\n  Got     : {}".format(len(inputs)))

    def test_that_the_outputs_attribute_of_a_node_is_a_mapping(self):
        n = Node()
        exception = None
        try:
            values = n.outputs.values()
        except AttributeError as e:
            exception = e
        ok_(exception is None,
            "\n  Test accessing `outputs.values()`" +
            " on {} having no inputs.".format(n) +
            "\n  Got unexpected exception:\n" +
            "\n      {}".format(feo(type(exception), exception)[0]))

    def test_that_nodes_do_not_get_undead_flows(self):
        """ Newly created nodes should only have flows assigned to them.

        A new node `n`, which re-used a previously used label `l`, retained the
        flows of those nodes which where labeled `l` before `n`. This incorrect
        behaviour is a problem if somebody wants to use different nodes with
        the same label in multiple energy systems. While this feature currently
        isn't used, it also lead to weird behaviour when running tests.

        This test ensures that new nodes only have those flows which are
        assigned to them on construction.
        """
        flow = object()
        old = Node(label="A reused label")
        bus = Bus(label="bus", inputs={old: flow})
        eq_(bus.inputs[old], flow,
            ("\n  Expected: {}" +
             "\n  Got     : {} instead").format(flow, bus.inputs[old]))
        eq_(old.outputs[bus], flow,
            ("\n  Expected: {}" +
             "\n  Got     : {} instead").format(flow, old.outputs[bus]))
        new = Node(label="A reused label")
        eq_(new.outputs, {},
            ("\n  Expected an empty dictionary of outputs." +
             "\n  Got: {} instead").format(new.outputs))


class EnergySystem_Nodes_Integration_Tests:

    def setup(self):
        self.es = ES()

    def test_node_registration(self):
        eq_(Node.registry, self.es)
        b1 = Bus(label='<B1>')
        eq_(self.es.entities[0], b1)
        b2 = Bus(label='<B2>')
        Transformer(label='<TF1>', inputs=[b1], outputs=[b2])
        ok_(isinstance(self.es.entities[2], Transformer))

