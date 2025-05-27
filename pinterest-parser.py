from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

# <br>Protected: False
# <br>Collaborators: <h1 id=tzt5u>Pins</h1><a href="https://www.pinterest.com/pin/613052568023623970/">https://www.pinterest.com/pin/613052568023623970/</a>

grammar = Grammar(
    r"""
    data           = (pins / garbage)+

    pins           = pin_section pin+

    pin_section    = ~r"<h1.*Pins</h1>"
    pin            = pin_open pin_url pin_data+
    pin_open       = ~r"<a href=\""
    pin_url        = ~r"https://www.pinterest.com/pin/" pin_id ~r".*" eol
    pin_id         = ~r"\d+"

    pin_data       = br pin_key ~": " no_data? pin_value_or_link? ~r"[,]?" br* eol?
    no_data        = ~r"No data,?"
    pin_key        = ~r"[^:]+"
    pin_value_or_link = pin_value / link
    pin_value      = ~r"[^\n<]+[^,\n<]"

    link           = ~r"<a href=\"" url ~r"\"[^>]*>[^<]*</a>"
    url            = ~r"https?://[^\"]+"
    eol            = ~r"[\s\n\r]+"
    br             = ~"<br>"
    garbage        = ~r"[\s\S]"
    """)

class PinterestVisitor(NodeVisitor):
  def visit_data(self, node, visited_children):
    for child in visited_children:
      if child[0] != []:
        return child[0]

  def visit_pins(self, node, visited_children):
    _, pins = visited_children
    output = {}
    for pin in pins:
      output.update(pin)
    return output

  def visit_pin(self, node, visited_children):
    output = {}
    _, pin_id, data = visited_children
    return {pin_id: dict(data)}

  def visit_pin_url(self, node, visited_children):
    _, pin_id, *_ = visited_children
    return pin_id.text

  def visit_pin_value_or_link(self, node, visited_children):
    return visited_children

  def visit_pin_value(self, node, visited_children):
    return node.text

  def visit_link(self, node, visited_children):
    _, url, *_ = node.children
    return url.text

  def visit_pin_data(self, node, visited_children):
    _, key, _, _, value, *_ = visited_children
    if key and value:
      return key.text, value[0][0]
    return key.text, ''

  def generic_visit(self, node, visited_children):
    """ The generic visit method. """
    if (node.expr_name.startswith("pin_")):
      return node
    else:
      return visited_children

parsed_data = grammar.parse(open("pinterest.html").read())

visitor = PinterestVisitor()

print(visitor.visit(parsed_data))
