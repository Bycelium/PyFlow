from qtpy.QtWidgets import QLabel
from qtpy.QtCore import Qt
from examples.example_calculator.calc_conf import register_node, OP_NODE_OUTPUT
from examples.example_calculator.calc_node_base import CalcNode, CalcGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("", self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setObjectName(self.node.content_label_objname)


@register_node(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    icon = "icons/out.png"
    op_code = OP_NODE_OUTPUT
    op_title = "Output"
    content_label_objname = "calc_node_output"

    GraphicsNode_class = CalcGraphicsNode
    NodeContent_class = CalcOutputContent

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.content.lbl.setText("%d" % val)
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return val
